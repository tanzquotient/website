#!/usr/bin/python
# -*- coding: UTF-8 -*-
from operator import pos

from django.conf import settings

from tq_website import settings as my_settings

from post_office import mail, models as post_office_models

from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site


def send_subscription_confirmation(subscription):
    context = {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
        'offering': subscription.course.offering.name,
    }

    if subscription.partner is not None:
        template = 'subscription_confirmation_with_partner'
        context.update({
            'partner_first_name': subscription.partner.first_name,
            'partner_last_name': subscription.partner.last_name,
        })
    elif subscription.course.type.couple_course:
        template = 'subscription_confirmation_without_partner'
    else:
        template = 'subscription_confirmation_without_partner_nocouple'

    _email_helper(subscription.user.email, template, context)


def send_participation_confirmation(subscription, connection=None):
    context = {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
        'offering': subscription.course.offering.name,
        'course_info': create_course_info(subscription)
    }

    if subscription.partner is not None:
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

    _email_helper(subscription.user.email, template, context)


def send_rejection(subscription, connection=None):
    context = {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
        'offering': subscription.course.offering.name,
    }

    # detect the reason why the subscription is rejected
    reason = 'unknown'
    if subscription.course.get_free_places_count() == 0:
        template = 'rejection_overbooked'
        reason = 'overbooked'
    elif subscription.course.type.couple_course and subscription.partner is None:
        template = 'rejection_no_partner'
        reason = 'no_partner'
    else:
        template = 'rejection_unknown_reason'

    _email_helper(subscription.user.email, template, context)

    return reason


def _email_helper(email, template, context):
    """Sending facility. Catches errors due to not existent template."""
    try:
        mail.send(
            [email, my_settings.EMAIL_HOST_USER],
            my_settings.DEFAULT_FROM_EMAIL,
            template=template,
            context=context,
        )
    except post_office_models.EmailTemplate.DoesNotExist:
        # since the post_office app does not check if a template exists, catch it here
        mail.send(
            [email, my_settings.EMAIL_HOST_USER],
            my_settings.DEFAULT_FROM_EMAIL,
            subject=u"Template missing!!!",
            message=u"Template for this Email was not found.\n\nPlease contact the administrator and report this issue.",
            context=context,
        )


def create_user_info(user):
    s = u'{}\n'.format(user.get_full_name())
    if user.email:
        s += user.email + "\n"
    if user.profile.phone_number:
        s += user.profile.phone_number + "\n"
    return s.strip('\n')


def create_course_info(subscription):
    course = subscription.course
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
        current_site = Site.objects.get_current().domain
        voucher_url = current_site+reverse('payment:voucherpayment_index', kwargs={'usi': subscription.usi})

        s += u'Kosten: {}\n'.format(course.format_prices())
        s += u'(Bitte bring das Kursgeld in die erste Tanzstunde passend mit. Hast du einen Gutschein? <a href="{}">Löse ihn vor Kursbeginn ein</a>.)\n'.format(
            voucher_url)
    return s.strip('\n')
