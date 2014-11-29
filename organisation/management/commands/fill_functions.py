# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import NoArgsCommand
from organisation.models import *
from django.contrib.auth.models import User
from courses.models import UserProfile
import os

class Command(NoArgsCommand):
    PROFILES_PATH = './static/profiles/'
    
    functions=[
               ["Präsident","praesident@tq.vseth.ch","irina"],
               ["Vizepräsident","vizepr@tq.vseth.ch","simon"],
               ["Quästor","quaestor@tq.vseth.ch","matthäus"],
               ["Produkte/Marketing","produktmarketing@tq.vseth.ch","hendrik"],
               ["Kommunikation","kommunikation@tq.vseth.ch","kelsey"],
               ["Eventmanagement","events@tq.vseth.ch","julian"],
               ["Tanzadministration","tanzen@tq.vseth.ch","marie"],
               ["IT","informatik@tq.vseth.ch","simon"]
    ]
    
    def handle_noargs(self, **options):
        for f in self.functions:
            user = User.objects.get(username=f[2])
            Function.objects.get_or_create(name=f[0], defaults={'email':f[1], 'user': user})
            
            fname = self.PROFILES_PATH+user.username+'.html'
            if os.path.isfile(fname):
                f = open(fname, 'r')
                UserProfile.objects.get_or_create(user=user, defaults={'about_me': f.read(),'student_status': 'eth'})
                f.close()
