#!/usr/bin/python
# -*- coding: UTF-8 -*-
          
from django.core.mail import send_mail
from django.conf import settings
from tq_website import settings as my_settings

SENDER = u'\n\nDein TQ\ntq.ethz.ch\nBei fragen wende dich an tanzen@tq.vseth.ch'
FOOTER = u'\n\nLiebe Grüsse & bis bald'+SENDER
FOOTER2 = u'\n\nWir freuen uns auf dich!'+SENDER
KURSGELD = u'Bitte bring das Kursgeld in die erste Tanzstunde passend mit.'

def send_subscription_confirmation(subscription):
    if subscription.partner != None:
        message = u'Hallo {}\n\nDu wurdest soeben für den Kurs {} im {} zusammen mit {} angemeldet. Das System hat deine Anmeldung aufgenommen, sie ist aber noch nicht definitiv. Du erhältst später eine Teilnahmebestätigung.'.format(subscription.user.first_name, subscription.course.type.name, subscription.course.offering.name, subscription.partner.first_name)+FOOTER
    elif subscription.course.type.couple_course:
        message = u'Hallo {}\n\nDu wurdest soeben für den Kurs {} im {} angemeldet. Das System hat deine Anmeldung aufgenommen, sie ist aber noch nicht definitiv.\nDa du dich alleine angemeldet hast, versuchen wir für dich einen Partner zu finden. Du erhältst dann eine Teilnahmebestätigung zusammen mit den Kontaktdaten deines Partners.'.format(subscription.user.first_name, subscription.course.type.name, subscription.course.offering.name)+FOOTER
    else:
        message = u'Hallo {}\n\nDu wurdest soeben für den Kurs {} im {} angemeldet. Das System hat deine Anmeldung aufgenommen, sie ist aber noch nicht definitiv. Du erhältst später eine Teilnahmebestätigung.'.format(subscription.user.first_name, subscription.course.type.name, subscription.course.offering.name)+FOOTER
        
    send_mail(create_subject(u'TQ Anmeldungseingang'), message, my_settings.EMAIL_HOST_USER,
        [subscription.user.email, my_settings.EMAIL_HOST_USER], fail_silently=False)
    
def send_participation_confirmation(subscription):
    if subscription.partner != None:
        message = u'Hallo {}\n\nDeine Teilnahme am Kurs {} im {} ist nun definitiv.\n'.format(subscription.user.first_name, subscription.course.type.name, subscription.course.offering.name)+create_user_info(subscription.partner)+u'\n'+create_course_info(subscription.course)+FOOTER2
    elif subscription.course.type.couple_course:
        message = u'Hallo {}\n\nDeine Teilnahme am Kurs {} im {} ist nun definitiv. Du nimmst alleine an einem Partnerkurs teil bzw. das System weiss nichts von deinem Partner. Sollte dies ein Fehler sein, melde dich bitte bei uns.\n\n'.format(subscription.user.first_name, subscription.course.type.name, subscription.course.offering.name)+create_course_info(subscription.course)+FOOTER2
    else:
        message = u'Hallo {}\n\nDeine Teilnahme am Kurs {} im {} ist nun definitiv.\n\n'.format(subscription.user.first_name, subscription.course.type.name, subscription.course.offering.name)+create_course_info(subscription.course)+FOOTER2

    send_mail(create_subject(u'TQ Teilnahmebestätigung'), message, my_settings.EMAIL_HOST_USER,
        [subscription.user.email], fail_silently=False)
    
def create_user_info(user):
    s=u'Die Kontaktdaten deines Partners sind:\n{}\n'.format(user.get_full_name())
    if user.email:
        s+=user.email+"\n"
    if user.profile.phone_number:
        s+=user.profile.phone_number+"\n"
    return s
    
    
def create_course_info(course):
    s = u'Nochmals alle Infos zum Kurs:\n{}\n{}, {}\n{}\n'.format(course.type.name, course.format_times(), course.room, course.get_period())
    if course.format_cancellations():
        s+=u'Ausfälle: {}\n'.format(course.format_cancellations())
    if course.format_prices:
        s+=u'Kosten: {}\n'.format(course.format_prices())
        s+=u'({})\n'.format(KURSGELD)
    return s

def create_subject(subject):
    s = u""
    # if settings.DEBUG:
    #    s += u"[DEBUG MODE] "
    s += subject
    return s
