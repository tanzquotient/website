#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.conf import settings

from tq_website import settings as my_settings

from post_office import mail

KURSGELD = u'Bitte bring das Kursgeld in die erste Tanzstunde passend mit.'


def send_subscription_confirmation(subscription):
    context = {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
        'offering': subscription.course.offering.name,
    }

    if subscription.partner != None:
        template = 'subscription_confirmation_with_partner'
        context.update({
            'partner_first_name': subscription.partner.first_name,
            'partner_last_name': subscription.partner.last_name,
        })
    elif subscription.course.type.couple_course:
        template = 'subscription_confirmation_without_partner'
    else:
        template = 'subscription_confirmation_without_partner_nocouple'

    mail.send(
        [subscription.user.email, my_settings.EMAIL_HOST_USER],
        my_settings.DEFAULT_FROM_EMAIL,
        template=template,
        context=context,
    )


def send_participation_confirmation(subscription, connection=None):
    context = {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
        'offering': subscription.course.offering.name,
        'course_info': create_course_info(subscription.course)
    }

    if subscription.partner != None:
        template = 'participation_confirmation_with_partner'
        context.update({
            'partner_first_name': subscription.partner.first_name,
            'partner_last_name': subscription.partner.last_name,
            'partner_info': create_user_info(subscription.partner),
        })
    elif subscription.course.type.couple_course:
        template = 'participation_confirmation_without_partner'
    else:
        template = 'participation_confirmation_without_partner_nocouple'

    mail.send(
        [subscription.user.email, my_settings.EMAIL_HOST_USER],
        my_settings.DEFAULT_FROM_EMAIL,
        template=template,
        context=context,
    )


def create_user_info(user):
    s = u'{}\n'.format(user.get_full_name())
    if user.email:
        s += user.email + "\n"
    if user.profile.phone_number:
        s += user.profile.phone_number + "\n"
    return s.strip('\n')


def create_course_info(course):
    s = u'{}\n{}'.format(course.type.name, course.format_lessons())
    if course.room:
        s += u', {}\n'.format(course.room)
    else:
        s += u'\n'
    if course.get_period():
        s += u'{}\n'.format(course.get_period())
    if course.format_cancellations():
        s += u'Ausfälle: {}\n'.format(course.format_cancellations())
    if course.format_prices:
        s += u'Kosten: {}\n'.format(course.format_prices())
        s += u'({})\n'.format(KURSGELD)
    return s.strip('\n')
