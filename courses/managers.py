from datetime import date

from django.db import models
from django.db.models import QuerySet
from parler.managers import TranslatableManager

from courses.models import SubscribeState, LeadFollow, MatchingState, Subscribe


class UserProfileManager(models.Manager):
    def get_queryset(self):
        return super(UserProfileManager, self).get_queryset().filter(user__is_active=True)


class CourseManager(TranslatableManager):
    def weekday(self, weekday):
        result_list = []
        for c in self.all():
            t = c.get_first_regular_lesson()
            common_irr_weekday = c.get_common_irregular_weekday()

            weekday_to_add = None
            if t is not None:
                weekday_to_add = t.weekday
            else:
                if common_irr_weekday is not None:
                    weekday_to_add = common_irr_weekday

            if weekday_to_add == weekday:
                result_list.append(c)
        return result_list

    def by_month(self):
        result = []
        courses = self.all()
        sorted_courses = sorted(courses,
                                key=lambda c: c.get_first_lesson_date() if c.get_first_lesson_date() else date(
                                    day=1, month=1, year=9999))
        current_date = date(year=1, month=1, day=1)
        unknown_list = []
        month_list = []
        for c in sorted_courses:
            first_date = c.get_first_lesson_date()
            if first_date is None and c.get_period() is not None:
                first_date = c.get_period().date_from

            if first_date:
                if current_date.year != first_date.year or current_date.month != first_date.month:
                    if month_list:
                        result.append((current_date, month_list))
                    # go to next month
                    current_date = first_date
                    month_list = []
                # just append to current month list
                month_list.append(c)
            else:
                unknown_list.append(c)
        if month_list:
            result.append((current_date, month_list))
        if unknown_list:
            result.append((None, unknown_list))
        return result


class AddressManager(models.Manager):
    def create_from_user_data(self, data):
        from courses.models import Address
        address = Address(street=data['street'], plz=data['plz'], city=data['city'])
        address.save()
        return address


class BankAccountManager(models.Manager):
    def create_from_user_data(self, data):
        from courses.models import BankAccount
        bank_account = BankAccount(iban=data['iban'], bank_name=data['bank_name'], bank_zip_code=data['bank_zip_code'],
                                   bank_city=data['bank_city'], bank_country=data['bank_country'])
        bank_account.save()
        return bank_account


# construction to allow chaining of queryset methods (chaining manager methods is not possible)
class SubscribeQuerySet(models.QuerySet):

    def leaders(self) -> QuerySet[Subscribe]:
        return self.active().filter(lead_follow=LeadFollow.LEAD)

    def followers(self) -> QuerySet[Subscribe]:
        return self.active().filter(lead_follow=LeadFollow.FOLLOW)

    def no_lead_follow_preference(self) -> QuerySet[Subscribe]:
        return self.active().filter(lead_follow=LeadFollow.NO_PREFERENCE)

    def single(self) -> QuerySet[Subscribe]:
        return self.active().filter(matching_state__in=MatchingState.SINGLE_STATES)

    def single_with_preference(self, lead_or_follow: str) -> QuerySet[Subscribe]:
        return self.active().filter(matching_state__in=MatchingState.SINGLE_STATES, lead_follow=lead_or_follow)

    def matched(self) -> QuerySet[Subscribe]:
        return self.active().filter(matching_state__in=MatchingState.MATCHED_STATES)

    def accepted(self) -> QuerySet[Subscribe]:
        return self.filter(state__in=SubscribeState.ACCEPTED_STATES)

    def active(self) -> QuerySet[Subscribe]:
        return self.exclude(state__in=SubscribeState.REJECTED_STATES)

    def paid(self) -> QuerySet[Subscribe]:
        return self.filter(state__in=SubscribeState.PAID_STATES)

    def course_payment(self) -> QuerySet[Subscribe]:
        from courses.models import PaymentMethod
        return self.filter(paymentmethod=PaymentMethod.COURSE)

    def voucher_payment(self) -> QuerySet[Subscribe]:
        from courses.models import PaymentMethod
        return self.filter(paymentmethod=PaymentMethod.VOUCHER)

    def online_payment(self) -> QuerySet[Subscribe]:
        from courses.models import PaymentMethod
        return self.filter(paymentmethod=PaymentMethod.ONLINE)

    def new(self) -> QuerySet[Subscribe]:
        return self.filter(state=SubscribeState.NEW)
