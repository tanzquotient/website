from django.db import models

from datetime import date
from parler.managers import TranslatableManager
from django.db.models import Q

class CourseManager(TranslatableManager):
    def weekday(self, weekday):
        result_list = []
        for c in self.all():
            t = c.get_first_regular_lesson()
            if (weekday == None and t == None) or (t != None and t.weekday == weekday):
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

    def live(self):
        return self.filter(state='published')

    def interesting(self):
        return self.filter(interesting=True)


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
        return self.filter(state__in=[Subscribe.State.CONFIRMED, Subscribe.State.PAYED, Subscribe.State.COMPLETED])

    def paid(self):
        from courses.models import Subscribe
        return self.filter(state__in=[Subscribe.State.PAYED, Subscribe.State.TO_REIMBURSE, Subscribe.State.COMPLETED])

    def course_payment(self):
        from courses.models import PaymentMethod
        return self.filter(paymentmethod=PaymentMethod.COURSE)

    def voucher_payment(self):
        from courses.models import PaymentMethod
        return self.filter(paymentmethod=PaymentMethod.VOUCHER)

    def new(self):
        from courses.models import Subscribe
        return self.filter(state=Subscribe.State.NEW)
