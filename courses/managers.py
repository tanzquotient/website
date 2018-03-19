from django.db import models

from datetime import date
from parler.managers import TranslatableManager
from django.db.models import Q

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
            fid = c.get_first_lesson_date()
            if fid:
                if current_date.year != fid.year or current_date.month != fid.month:
                    if month_list:
                        result.append((current_date, month_list))
                    # go to next month
                    current_date = fid
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


class PlannedCourseManager(CourseManager):
    def get_queryset(self):
        from courses.services import get_subsequent_offering
        return super(PlannedCourseManager, self).get_queryset().filter(offering=get_subsequent_offering())


class CurrentCourseManager(CourseManager):
    def get_queryset(self):
        from courses.services import get_current_active_offering
        return super(CurrentCourseManager, self).get_queryset().filter(offering=get_current_active_offering())


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
# read https://www.google.ch/url?sa=t&rct=j&q=&esrc=s&source=web&cd=2&cad=rja&uact=8&ved=0ahUKEwjOlbrz1-_LAhVHPRQKHXkqD-EQygQIKjAB&url=https%3A%2F%2Fdocs.djangoproject.com%2Fen%2F1.9%2Ftopics%2Fdb%2Fmanagers%2F%23using-managers-for-related-object-access&usg=AFQjCNEJzw5qfnl5vQoOrHbtdK-iaxkG7g&sig2=lC0IkWiubBDk9C0iAjj7Iw
# and read http://stackoverflow.com/questions/6067195/how-does-use-for-related-fields-work-in-django
class SubscribeQuerySet(models.QuerySet):
    def men(self):
        from courses.models import UserProfile
        return self.filter(user__profile__gender=UserProfile.Gender.MEN)

    def women(self):
        from courses.models import UserProfile
        return self.filter(user__profile__gender=UserProfile.Gender.WOMAN)

    def single_men(self):
        from courses.models import UserProfile
        return self.filter(partner__isnull=True, user__profile__gender=UserProfile.Gender.MEN)

    def single_women(self):
        from courses.models import UserProfile
        return self.filter(partner__isnull=True, user__profile__gender=UserProfile.Gender.WOMAN)

    def accepted(self):
        from courses.models import Subscribe
        return self.filter(state__in=Subscribe.State.ACCEPTED_STATES)

    def active(self):
        from courses.models import Subscribe
        return self.exclude(state__in=Subscribe.State.REJECTED_STATES)

    def paid(self):
        from courses.models import Subscribe
        return self.filter(state__in=Subscribe.State.PAID_STATES)

    def course_payment(self):
        from courses.models import PaymentMethod
        return self.filter(paymentmethod=PaymentMethod.COURSE)

    def voucher_payment(self):
        from courses.models import PaymentMethod
        return self.filter(paymentmethod=PaymentMethod.VOUCHER)

    def online_payment(self):
        from courses.models import PaymentMethod
        return self.filter(paymentmethod=PaymentMethod.ONLINE)

    def new(self):
        from courses.models import Subscribe
        return self.filter(state=Subscribe.State.NEW)
