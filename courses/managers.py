from django.db import models

import datetime

from django.conf import settings

import django.contrib.auth as auth

from models import *

class CourseManager(models.Manager):
    def weekday(self, weekday):
        result_list = []
        for c in self.all():
            t = c.get_first_time()
            if (weekday==None and t==None) or (t !=None and t.weekday==weekday):
                result_list.append(c)
        return result_list