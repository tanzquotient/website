from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Optional

from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q, Model, ForeignKey, PROTECT, TextField, CharField, DateTimeField, DecimalField
from django.utils.translation import gettext_lazy as _
from reversion import revisions as reversion

from courses import managers
from utils import CodeGenerator
from . import MatchingState, SubscribeState, PaymentMethod, LeadFollow, Offering, StudentStatus, PriceReduction


@reversion.register()
class Subscribe(Model):
    # Identifying data
    user = ForeignKey(to=User, related_name='subscriptions', on_delete=PROTECT)
    course = ForeignKey('Course', related_name='subscriptions', on_delete=PROTECT)

    # Partner, matching, lead/follow preference
    partner = ForeignKey(User, related_name='subscriptions_as_partner', blank=True, null=True, on_delete=PROTECT)
    matching_state = CharField(max_length=30, blank=False, null=False, db_index=True, choices=MatchingState.CHOICES,
                               default=MatchingState.UNKNOWN)
    lead_follow = CharField(max_length=1, blank=False, null=False, default=LeadFollow.NO_PREFERENCE,
                            choices=LeadFollow.CHOICES)

    # Experience and comment
    experience = TextField(blank=True, null=True)
    comment = TextField(blank=True, null=True)
    comment.help_text = 'A optional comment made by the user during subscription.'

    # Timestamp and State
    date = DateTimeField(blank=False, null=False, auto_now_add=True)
    date.help_text = 'The date/time when the subscription was made.'
    state = CharField(max_length=30, blank=False, null=False, db_index=True, choices=SubscribeState.CHOICES,
                      default=SubscribeState.NEW)

    # Payment stuff
    usi = CharField(max_length=6, blank=True, null=False, default=CodeGenerator.short_uuid_without_ambiguous_characters, unique=True)
    usi.help_text = 'Unique subscription identifier: Randomly generated'
    price_to_pay = DecimalField(blank=True, null=True, default=None, decimal_places=2, max_digits=6)
    paymentmethod = CharField(max_length=30, choices=PaymentMethod.CHOICES, blank=True, null=True)

    # Objects
    objects = managers.SubscribeQuerySet.as_manager()

    def generate_usi(self) -> str:
        if self.usi:
            return self.usi  # Be sure to not regenerate USI
        usi = CodeGenerator.short_uuid_without_ambiguous_characters()
        return usi if not Subscribe.objects.filter(usi=usi).exists() else self.generate_usi()

    def is_active(self) -> bool:
        return self.state not in SubscribeState.REJECTED_STATES

    def is_matched(self) -> bool:
        return self.is_active() and self.matching_state in MatchingState.MATCHED_STATES

    def is_single_with_preference(self, lead_or_follow: str) -> bool:
        return self.is_active() and self.matching_state in MatchingState.TO_MATCH_STATES \
               and self.lead_follow == lead_or_follow

    def get_offering(self) -> Offering:
        return self.course.offering

    get_offering.short_description = 'Offering'

    def get_user_gender(self) -> str:
        return self.user.profile.gender

    get_user_gender.short_description = 'Gender'

    def get_user_email(self) -> str:
        return self.user.email

    get_user_email.short_description = 'Email'

    def get_user_mobile(self) -> str:
        return self.user.profile.phone_number

    get_user_mobile.short_description = 'Mobile'

    def get_user_body_height(self) -> int:
        return self.user.profile.body_height

    get_user_body_height.short_description = 'Body height'

    def get_user_student_status(self) -> str:
        return self.user.profile.student_status

    get_user_student_status.short_description = 'Student'

    def get_calculated_experience(self) -> str:
        """returns similar courses that the user did before in the system"""
        from ..services.general import calculate_relevant_experience

        preceding_courses_done = []
        for predecessor in self.course.preceding_courses.all():
            preceding_courses_done += [s.course for s in
                                       predecessor.subscriptions.accepted().filter(user=self.user).all()]
        relevant_courses_done = [c for c in calculate_relevant_experience(self.user, self.course) if
                                 c not in preceding_courses_done]

        preceding_courses_str = ', '.join(map(str, preceding_courses_done))
        relevant_courses_str = ', '.join(map(str, relevant_courses_done))
        return "{} / ...{}".format(preceding_courses_str, relevant_courses_str)

    get_calculated_experience.short_description = "Calculated experience"

    """"
    ----------------------------------------------------------------
    Payment
    ----------------------------------------------------------------
    """

    def paid(self) -> bool:
        if self.state in SubscribeState.PAID_STATES:
            return True

        # If open amount == 0, but not reflected in self.state
        if self.open_amount().is_zero():
            return self.mark_as_paid(self.paymentmethod)

    def is_payment_overdue(self) -> bool:
        if self.paid() or self.state not in SubscribeState.TO_PAY_STATES:
            return False

        return self.course.is_over() and (self.course.offering is None or self.course.offering.is_over())

    @admin.action(description='Paid?')
    def get_payment_state(self) -> str:
        """searches for courses that the user did before in the system"""
        c = self.user.subscriptions.filter(state=SubscribeState.CONFIRMED, course__offering__active=False).filter(
            ~Q(course=self.course)).count()
        if self.paid():
            r = 'Yes'
        else:
            r = 'No'

        if c > 0:
            # this user didn't pay for other courses
            r += ', owes {} more'.format(c)
        return r

    def mark_as_paid(self, payment_method, user=None) -> bool:
        if self.state == SubscribeState.CONFIRMED:

            with reversion.create_revision():
                self.state = SubscribeState.PAID
                self.paymentmethod = payment_method
                self.save()
                if user is not None:
                    reversion.set_user(user)
                reversion.set_comment(f'Paid using payment method {payment_method}')
            if self.paymentmethod == PaymentMethod.ONLINE:
                from courses.emailcenter import send_online_payment_successful
                send_online_payment_successful(self)
            return True
        else:
            return False

    def _compute_price_to_pay(self) -> Decimal:
        if self.user.profile.is_student():
            return self.course.price_with_legi or Decimal(0)
        return self.course.price_without_legi or Decimal(0)

    def generate_price_to_pay(self) -> None:
        self.price_to_pay = self._compute_price_to_pay()

    def get_price_to_pay(self) -> Decimal:
        if self.price_to_pay is None:
            self.generate_price_to_pay()
            self.save()
        return Decimal(self.price_to_pay)

    def price_after_reductions(self) -> Decimal:
        return self.get_price_to_pay() - self.sum_of_reductions()

    def sum_of_reductions(self) -> Decimal:
        sum_of_reductions = Decimal(0)

        # Add up reductions
        for price_reduction in self.price_reductions.all():
            sum_of_reductions += price_reduction.amount

        return sum_of_reductions

    def sum_of_payments(self) -> Decimal:
        sum_of_payments = 0

        # Add subscription payments
        for payment in self.subscription_payments.all():
            sum_of_payments += payment.amount

        return Decimal(sum_of_payments)

    def open_amount(self) -> Decimal:
        if self.state in SubscribeState.PAID_STATES:
            return Decimal(0)

        open_amount = self.price_after_reductions() - self.sum_of_payments()

        # Open amount is non-negative
        return max(Decimal(0), open_amount)

    def apply_price_reduction(self, amount: Decimal, voucher, user: Optional[User] = None) -> Decimal:
        PriceReduction.objects.create(subscription=self, amount=amount, used_voucher=voucher,
                                      comment=f"Applied voucher {voucher.key}")

        open_amount = self.open_amount()
        if open_amount.is_zero():
            self.mark_as_paid(PaymentMethod.VOUCHER, user)

        return open_amount

    def get_last_payment_reminder(self) -> Optional[datetime.date]:
        q = self.payment_reminders
        if q.count():
            return q.first().date
        else:
            return None

    """"
    ----------------------------------------------------------------
    Partner & Matching
    ----------------------------------------------------------------
    """

    def derive_matching_state(self) -> None:
        """derives the matching state from the current information (if couple course and if partner set or not)"""
        if self.course.type.couple_course:
            if self.partner is None:
                if self.matching_state not in [MatchingState.TO_MATCH, MatchingState.TO_REMATCH]:
                    self.matching_state = MatchingState.TO_MATCH
            else:
                if self.matching_state in [MatchingState.TO_MATCH, MatchingState.TO_REMATCH]:
                    self.matching_state = MatchingState.MATCHED
        else:
            self.matching_state = MatchingState.NOT_REQUIRED
            # DO NOT save here since this method is also called from save()

    def get_partner_name(self) -> Optional[str]:
        if not self.partner:
            return None
        return f"{self.partner.first_name} {self.partner.last_name}"

    def get_assigned_role_str(self) -> str:
        role = self.assigned_role()
        if role == LeadFollow.NO_PREFERENCE:
            return str(_('no preference'))
        if not self.was_role_assigned():
            if role == LeadFollow.LEAD:
                return str(_('leader'))
            return str(_('follower'))
        else:
            if role == LeadFollow.LEAD:
                return str(_('no preference, assigned as leader'))
            return str(_('no preference, assigned as follower'))

    def assigned_role(self) -> str:

        # User specified role
        if self.lead_follow != LeadFollow.NO_PREFERENCE:
            return self.lead_follow

        # Role specified by partner
        partner_subscription = self.get_partner_subscription()
        if partner_subscription is not None:
            return LeadFollow.partner(partner_subscription.lead_follow)
        
        # No role specified and no partner
        return LeadFollow.NO_PREFERENCE
        
    def is_role_specified(self) -> bool:
        return self.assigned_role() != LeadFollow.NO_PREFERENCE

    def was_role_assigned(self) -> bool:
        return self.lead_follow == LeadFollow.NO_PREFERENCE and self.assigned_role() != LeadFollow.NO_PREFERENCE

    def get_partner_subscription(self) -> Optional[Subscribe]:
        if self.partner is None:
            return None

        partner_subscription_query = self.course.subscriptions.filter(user=self.partner)
        if partner_subscription_query.count() == 1:
            return partner_subscription_query.get()

    def clean(self) -> None:
        # Don't allow subscriptions with partner equals to subscriber
        if self.partner == self.user:
            raise ValidationError('Subscriptions with yourself as the partner are not allowed.')

    def save(self, *args, **kwargs) -> None:
        self.derive_matching_state()
        if not self.usi:
            self.usi = self.generate_usi()
        if not self.price_to_pay:
            self.generate_price_to_pay()
        super(Subscribe, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        if self.state != SubscribeState.NEW:
            messages.add_message(None, messages.ERROR, 'Cannot delete non-NEW subscription.')
        else:
            super(Subscribe, self).delete(*args, **kwargs)

    def __str__(self) -> str:
        return '{} subscribes to {}'.format(self.user.get_full_name(), self.course)
