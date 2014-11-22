# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import NoArgsCommand
from organisation.models import *
from django.contrib.auth.models import User

class Command(NoArgsCommand):
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
            Function.objects.get_or_create(name=f[0], defaults={'email':f[1], 'user': User.objects.get(username=f[2])})
