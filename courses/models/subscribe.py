import hashlib

import base36
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from reversion import revisions as reversion
from django.utils.translation import gettext_lazy as _


from courses import managers
from . import MatchingState, SubscribeState, PaymentMethod, LeadFollow


@reversion.register()
class Subscribe(models.Model):
    # Identifying data
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='subscriptions', on_delete=models.PROTECT)
    course = models.ForeignKey('Course', related_name='subscriptions', on_delete=models.PROTECT)

    # Partner, matching, lead/follow preference
    partner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, related_name='subscriptions_as_partner', blank=True,
        null=True, on_delete=models.PROTECT)
    matching_state = models.CharField(
        max_length=30, blank=False, null=False, db_index=True,
        choices=MatchingState.CHOICES, default=MatchingState.UNKNOWN)
    lead_follow = models.CharField(
        max_length=1, blank=False, null=False,
        default=LeadFollow.NO_PREFERENCE, choices=LeadFollow.CHOICES)

    # Experience and comment
    experience = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    comment.help_text = 'A optional comment made by the user during subscription.'

    # Timestamp and State
    date = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    date.help_text = 'The date/time when the subscription was made.'
    state = models.CharField(max_length=30, blank=False, null=False, db_index=True,
                             choices=SubscribeState.CHOICES, default=SubscribeState.NEW)

    # Payment stuff
    usi = models.CharField(max_length=6, blank=True, null=False, default="------", unique=True)
    usi.help_text = 'Unique subscription identifier: 4 characters identifier, 2 characters checksum'
    price_to_pay = models.FloatField(blank=True, null=True, default=None)
    paymentmethod = models.CharField(max_length=30, choices=PaymentMethod.CHOICES, blank=True, null=True)

    # Objects
    objects = managers.SubscribeQuerySet.as_manager()

    def generate_usi(self):
        checksum = hashlib.md5()
        checksum.update(str(self.id).encode('utf-8'))
        return (base36.dumps(self.id).zfill(4)[:4] + checksum.hexdigest()[:2]).lower()

    def get_offering(self):
        return self.course.offering

    get_offering.short_description = 'Offering'

    def get_user_gender(self):
        return self.user.profile.gender

    get_user_gender.short_description = 'Gender'

    def get_user_email(self):
        return self.user.email

    get_user_email.short_description = 'Email'

    def get_user_mobile(self):
        return self.user.profile.phone_number

    get_user_mobile.short_description = 'Mobile'

    def get_user_body_height(self):
        return self.user.profile.body_height

    get_user_body_height.short_description = 'Body height'

    def get_user_student_status(self):
        return self.user.profile.student_status

    get_user_student_status.short_description = 'Student'

    def get_calculated_experience(self):
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

    def payed(self):
        return self.state in SubscribeState.PAID_STATES

    def get_payment_state(self):
        """searches for courses that the user did before in the system"""
        c = self.user.subscriptions.filter(state=SubscribeState.CONFIRMED, course__offering__active=False).filter(
            ~Q(course=self.course)).count()
        if self.payed():
            r = 'Yes'
        else:
            r = 'No'

        if c > 0:
            # this user didn't pay for other courses
            r += ', owes {} more'.format(c)
        return r

    get_payment_state.short_description = 'Paid?'

    def mark_as_paid(self, payment_method, user=None):
        if self.state == SubscribeState.CONFIRMED:

            with reversion.create_revision():
                self.state = SubscribeState.PAID
                self.paymentmethod = payment_method
                self.save()
                if user is not None:
                    reversion.set_user(user)
                reversion.set_comment('Paid using payment method ' + payment_method)
            if self.paymentmethod == PaymentMethod.ONLINE:
                from courses.emailcenter import send_online_payment_successful
                send_online_payment_successful(self)
            return True
        else:
            return False

    def apply_voucher(self, voucher, user=None):
        price = self.get_price_to_pay()
        with reversion.create_revision():
            voucher_value = price * (float(voucher.percentage) / 100.0)
            self.price_to_pay = price - voucher_value
            if price == voucher_value and self.state == SubscribeState.CONFIRMED:
                self.state = SubscribeState.PAID
                self.paymentmethod = PaymentMethod.VOUCHER
                if user is not None:
                    reversion.set_user(user)
                reversion.set_comment('Paid using payment method ' + PaymentMethod.VOUCHER)
                from courses.emailcenter import send_online_payment_successful
                send_online_payment_successful(self)
            self.save()

        return price == voucher_value

    def generate_price_to_pay(self):
        if self.user.profile.student_status == 'no':
            self.price_to_pay = self.course.price_without_legi
        else:
            self.price_to_pay = self.course.price_with_legi
        # happens when course has no price(s) set
        if self.price_to_pay is None:
            self.price_to_pay = 0

    def get_price_to_pay(self):
        if not self.price_to_pay:
            self.generate_price_to_pay()
            self.save()
        return self.price_to_pay

    def derive_matching_state(self):
        """derives the matching state from the current information (if couple course and if partner set or not)"""
        if self.course.type.couple_course:
            if self.partner is None:
                if self.matching_state not in [MatchingState.TO_MATCH, MatchingState.TO_REMATCH]:
                    self.matching_state = MatchingState.TO_MATCH
            else:
                if self.matching_state in [MatchingState.TO_MATCH, MatchingState.TO_REMATCH]:
                    self.matching_state = MatchingState.MATCHED
        else:
            self.matching_state = 'not_required'
            # DO NOT save here since this method is also called from save()

    def get_last_payment_reminder(self):
        q = self.payment_reminders
        if q.count():
            return q.first().date
        else:
            return None

    def get_partner_name(self):
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

    def assigned_role(self):

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

    def partner_subscription(self):
        if self.partner is None:
            return None

        partner_subscription_query = self.course.subscriptions.filter(user=self.partner)
        if partner_subscription_query.count() == 1:
            return partner_subscription_query.get()

    def clean(self):
        # Don't allow subscriptions with partner equals to subscriber
        if self.partner == self.user:
            raise ValidationError('Subscriptions with yourself as the partner are not allowed.')

    def save(self, *args, **kwargs):
        self.derive_matching_state()
        super(Subscribe, self).save(*args, **kwargs)  # ensure id is set
        self.usi = self.generate_usi()
        if not self.price_to_pay:
            self.generate_price_to_pay()
        super(Subscribe, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.state != SubscribeState.NEW:
            messages.add_message(None, messages.ERROR, 'Cannot delete non-NEW subscription.')
        else:
            super(Subscribe, self).delete(*args, **kwargs)

    def __str__(self):
        return '{} subscribes to {}'.format(self.user.get_full_name(), self.course)
