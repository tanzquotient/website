from operator import pos

from django.conf import settings

from tq_website import settings as my_settings

from post_office import mail, models as post_office_models

from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

import courses.models

from tq_website import settings as my_settings

import logging

log = logging.getLogger('tq')


def send_subscription_confirmation(subscription):
    context = {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
        'offering': subscription.course.offering.name,
        'course_info': create_course_info(subscription.course),
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

    return _email_helper(subscription.user.email, template, context)


def send_participation_confirmation(subscription):
    conf = my_settings.PAYMENT_ACCOUNT['default']
    current_site = Site.objects.get_current().domain
    voucher_url = current_site + reverse('payment:voucherpayment_index', kwargs={'usi': subscription.usi})

    context = {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
        'offering': subscription.course.offering.name,
        'course_info': create_course_info(subscription.course),
        'usi': subscription.usi,
        'account_IBAN': conf['IBAN'],
        'account_recipient': ','.join(conf['recipient']) if isinstance(conf['recipient'], (list, tuple)) else conf[
            'recipient'],
        'account_post_number': conf['post_number'] or '-',
        'voucher_url': voucher_url
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

    return _email_helper(subscription.user.email, template, context)


def send_online_payment_successful(subscription):
    context = {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
        'offering': subscription.course.offering.name,
    }

    template = 'online_payment_successful'

    return _email_helper(subscription.user.email, template, context)


def send_rejection(subscription, reason):
    context = {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
        'offering': subscription.course.offering.name,
    }

    template = 'rejection_{}'.format(reason)

    return _email_helper(subscription.user.email, template, context)


def send_teacher_welcome(teach):
    teacher = teach.teacher
    if not teacher.email:
        return None
    course = teach.course

    current_site = Site.objects.get_current().domain
    room_url = current_site + reverse('courses:subscription', kwargs={'course_id': course.id})
    coursepayment_url = current_site + reverse('payment:coursepayment_detail', kwargs={'course': course.id})
    login_url = current_site + reverse('account_login')

    context = {
        'first_name': teacher.first_name,
        'last_name': teacher.last_name,
        'course': course.type.name,
        'course_internal_name': course.name,
        'offering': course.offering.name,
        'course_info': create_course_info(course),
        'room_url': room_url,
        'room_info': course.room.description,
        'room_instructions': course.room.instructions,
        'coursepayment_url': coursepayment_url,
        'login_url': login_url,
    }

    template = 'teacher_welcome'

    return _email_helper(teacher.email, template, context)


def detect_rejection_reason(subscription):
    """
    detect the reason why the subscription is rejected
    :return: the reason as constant from Rejection.Reason
    """
    reason = courses.models.Rejection.Reason.UNKNOWN
    counts = subscription.course.get_free_places_count()
    if counts and counts['total'] == 0:
        reason = courses.models.Rejection.Reason.OVERBOOKED
    elif subscription.course.type.couple_course and subscription.partner is None:
        reason = courses.models.Rejection.Reason.NO_PARTNER
    return reason


def _email_helper(email, template, context):
    """Sending facility. Catches errors due to not existent template."""
    try:
        return mail.send(
            [email, my_settings.DEFAULT_FROM_EMAIL],
            my_settings.DEFAULT_FROM_EMAIL,
            template=template,
            context=context,
        )
    except post_office_models.EmailTemplate.DoesNotExist as e:
        log.error("Email Template missing with name: {}".format(template))
        return None


def create_user_info(user):
    s = '{}\n'.format(user.get_full_name())
    if user.email:
        s += user.email + "\n"
    if user.profile.phone_number:
        s += user.profile.phone_number + "\n"
    return s.strip('\n')


def create_course_info(course):
    s = '{}\n{}'.format(course.type.name, course.format_lessons())
    if course.room:
        s += ', {}\n'.format(course.room)
    else:
        s += '\n'
    if course.get_period() and course.offering and course.offering.type == courses.models.Offering.Type.REGULAR:
        s += '{}\n'.format(course.get_period())
    if course.format_cancellations():
        s += 'Ausfälle: {}\n'.format(course.format_cancellations())
    if course.format_prices:
        s += 'Kosten: {}\n'.format(course.format_prices())
    return s.strip('\n')
