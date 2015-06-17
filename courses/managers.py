from django.db import models

import datetime
import calendar

from django.conf import settings

import django.contrib.auth as auth

import models as my_models


class CourseManager(models.Manager):
    def weekday(self, weekday):
        result_list = []
        for c in self.all():
            t = c.get_first_regular_lesson()
            if (weekday == None and t == None) or (t != None and t.weekday == weekday):
                result_list.append(c)
        return result_list

    def by_month(self):
        result_dict = {}
        courses = self.all()
        sorted_courses = sorted(courses, key=lambda c: c.get_first_lesson_date() if c.get_first_lesson_date() else datetime.date(day=1,month=1,year=9999))
        current_date = datetime.date(year=1, month=1, day=1)
        unknown_list = []
        month_list = []
        for c in sorted_courses:
            fid = c.get_first_lesson_date()
            if fid:
                if current_date.year != fid.year or current_date.month != fid.month:
                    if month_list:
                        result_dict[current_date]=month_list
                    # go to next month
                    current_date = fid
                    month_list = []
                # just append to current month list
                month_list.append(c)
            else:
                unknown_list.append(c)
        if month_list:
            result_dict[current_date]=month_list
        if unknown_list:
            result_dict[datetime.date(year=9999,month=1,day=1)] = unknown_list
        return result_dict


class AddressManager(models.Manager):
    def create_from_user_data(self, data):
        address = my_models.Address(street=data['street'], plz=data['plz'], city=data['city'])
        address.save()
        return address


class SubscribeManager(models.Manager):
    def men(self):
        return self.filter(user__profile__gender='m')

    def women(self):
        return self.filter(user__profile__gender='w')

    def single_men(self):
        return self.filter(partner__isnull=True, user__profile__gender='m')

    def single_women(self):
        return self.filter(partner__isnull=True, user__profile__gender='w')
