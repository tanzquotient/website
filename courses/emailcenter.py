#!/usr/bin/python
# -*- coding: UTF-8 -*-
          
from django.core.mail import send_mail
from django.conf import settings

def send_subscription_confirmation(subscription):
    send_mail(create_subject(u'Anmeldungseingang beim TQ'), u'Hallo {}\nDu hast dich soeben für den Kurs {} im {} angemeldet. Das System hat deine Anmeldung aufgenommen, sie ist aber noch nicht definitiv. Du erhältst später eine Anmeldungsbestätigung.\n Liebe Grüsse & bis bald\n Dein TQ'.format(subscription.user.first_name, subscription.course.type.name, subscription.course.offering.name), 'anmeldungen@tq.vseth.ethz.ch',
        ['anmeldungen@tq.vseth.ethz.ch', subscription.user.email], fail_silently=False)
    
def create_subject(subject):
    s = u""
    if settings.DEBUG:
        s+=u"[DEBUG MODE]"
    s+=subject
