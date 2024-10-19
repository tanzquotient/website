from datetime import date

from django.db import models
from django.db.models import QuerySet
from parler.managers import TranslatableManager

from courses.models import SubscribeState, LeadFollow, MatchingState


class UserProfileManager(models.Manager):
    def get_queryset(self):
        return (
            super(UserProfileManager, self).get_queryset().filter(user__is_active=True)
        )


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
        sorted_courses = sorted(
            courses,
            key=lambda c: (
                c.get_first_lesson_date()
                if c.get_first_lesson_date()
                else date(day=1, month=1, year=9999)
            ),
        )
        current_date = date(year=1, month=1, day=1)
        month_list = []
        for c in sorted_courses:
            first_date = c.get_first_lesson_date() or c.get_period().date_from

            if (
                current_date.year != first_date.year
                or current_date.month != first_date.month
            ):
                if month_list:
                    result.append((current_date, month_list))
                # go to next month
                current_date = first_date
                month_list = []
            # just append to current month list
            month_list.append(c)

        if month_list:
            result.append((current_date, month_list))

        return result


class AddressManager(models.Manager):
    def create_from_user_data(self, data):
        from courses.models import Address

        address = Address(street=data["street"], plz=data["plz"], city=data["city"])
        address.save()
        return address


class BankAccountManager(models.Manager):
    def create_from_user_data(self, data):
        from courses.models import BankAccount

        bank_account = BankAccount(
            iban=data["iban"],
            bank_name=data["bank_name"],
            bank_zip_code=data["bank_zip_code"],
            bank_city=data["bank_city"],
            bank_country=data["bank_country"],
        )
        bank_account.save()
        return bank_account


# construction to allow chaining of queryset methods (chaining manager methods is not possible)
class SubscribeQuerySet(models.QuerySet):
    def leaders(self) -> QuerySet:
        return self.active().filter(lead_follow=LeadFollow.LEAD)

    def followers(self) -> QuerySet:
        return self.active().filter(lead_follow=LeadFollow.FOLLOW)

    def no_lead_follow_preference(self) -> QuerySet:
        return self.active().filter(lead_follow=LeadFollow.NO_PREFERENCE)

    def to_match(self) -> QuerySet:
        return self.admitted().filter(matching_state__in=MatchingState.TO_MATCH_STATES)

    def single(self) -> QuerySet:
        return self.active().filter(matching_state__in=MatchingState.SINGLE_STATES)

    def single_with_preference(self, lead_or_follow: str) -> QuerySet:
        return self.active().filter(
            matching_state__in=MatchingState.SINGLE_STATES, lead_follow=lead_or_follow
        )

    def matched(self) -> QuerySet:
        return self.active().filter(matching_state__in=MatchingState.MATCHED_STATES)

    def waiting_list(self) -> QuerySet:
        return self.filter(state=SubscribeState.WAITING_LIST).order_by("date")

    def accepted(self) -> QuerySet:
        return self.filter(state__in=SubscribeState.ACCEPTED_STATES)

    def active(self) -> QuerySet:
        return self.exclude(state__in=SubscribeState.REJECTED_STATES)

    def admitted(self) -> QuerySet:
        return self.active().exclude(state=SubscribeState.WAITING_LIST)

    def paid(self) -> QuerySet:
        return self.filter(state__in=SubscribeState.PAID_STATES)

    def course_payment(self) -> QuerySet:
        from courses.models import PaymentMethod

        return self.filter(paymentmethod=PaymentMethod.COURSE)

    def voucher_payment(self) -> QuerySet:
        from courses.models import PaymentMethod

        return self.filter(paymentmethod=PaymentMethod.VOUCHER)

    def online_payment(self) -> QuerySet:
        from courses.models import PaymentMethod

        return self.filter(paymentmethod=PaymentMethod.ONLINE)

    def new(self) -> QuerySet:
        return self.filter(state=SubscribeState.NEW)


class CourseTypeManager(TranslatableManager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().order_by("translations__title").distinct()


class LessonOccurrenceQuerySet(models.QuerySet):
    def without_teachers(self) -> QuerySet:
        return self.filter(teachers=None)
