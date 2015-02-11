#!/usr/bin/python
# -*- coding: UTF-8 -*-
          
from django.core.mail import send_mail
from django.conf import settings
from tq_website import settings as my_settings

def send_subscription_confirmation(subscription):
    if subscription.partner != None:
        message = add_footer(u'Hallo {}\n\nDu wurdest soeben für den Kurs {} im {} zusammen mit {} angemeldet. Das System hat deine Anmeldung aufgenommen, sie ist aber noch nicht definitiv. Du erhältst später eine Anmeldungsbestätigung.').format(subscription.user.first_name, subscription.course.type.name, subscription.course.offering.name, subscription.partner.first_name)
    elif subscription.course.type.couple_course:
        message = add_footer(u'Hallo {}\n\nDu wurdest soeben für den Kurs {} im {} angemeldet. Das System hat deine Anmeldung aufgenommen, sie ist aber noch nicht definitiv.\nDa du dich alleine angemeldet hast, versuchen wir für dich einen Partner zu finden. Du erhältst dann eine Anmeldungsbestätigung zusammen mit den Kontaktdaten deines Partners.').format(subscription.user.first_name, subscription.course.type.name, subscription.course.offering.name)
    else:
        message = add_footer(u'Hallo {}\n\nDu wurdest soeben für den Kurs {} im {} angemeldet. Das System hat deine Anmeldung aufgenommen, sie ist aber noch nicht definitiv. Du erhältst später eine Anmeldungsbestätigung.').format(subscription.user.first_name, subscription.course.type.name, subscription.course.offering.name)

    send_mail(create_subject(u'TQ Anmeldungseingang'), message, my_settings.EMAIL_HOST_USER,
        [my_settings.EMAIL_HOST_USER, subscription.user.email], fail_silently=False)
    
def create_subject(subject):
    s = u""
    if settings.DEBUG:
        s += u"[DEBUG MODE] "
    s += subject
    return s

def add_footer(message):
    return message + u'\n\nLiebe Grüsse & bis bald\n\nDein TQ\ntq.ethz.ch\nBei fragen wende dich an tanzen@tq.vseth.ch'
