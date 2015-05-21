from django.db import models

import datetime

from django.conf import settings

import django.contrib.auth as auth

import models as my_models


class CourseManager(models.Manager):
    def weekday(self, weekday):
        result_list = []
        for c in self.all():
            t = c.get_first_time()
            if (weekday == None and t == None) or (t != None and t.weekday == weekday):
                result_list.append(c)
        return result_list


class AddressManager(models.Manager):
    def create_from_user_data(self, data):
        address = my_models.Address(street=data['street'], plz=data['plz'], city=data['city'])
        address.save()
        return address


class SubscribeManager(models.Manager):
    def single_men(self):
        return self.filter(partner__isnull=True, user__profile__gender='m')

    def single_women(self):
        return self.filter(partner__isnull=True, user__profile__gender='w')
