import logging

from django.contrib.sites.models import Site
from django.urls import reverse
from post_office import mail, models as post_office_models

import courses.models
from tq_website import settings as my_settings

log = logging.getLogger('tq')


def send_subscription_confirmation(subscription):
    context = {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
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


def _build_subscription_context(subscription):
    from payment import payment_processor
    conf = my_settings.PAYMENT_ACCOUNT['default']
    current_site = Site.objects.get_current().domain
    voucher_url = current_site + reverse('payment:voucherpayment_index', kwargs={'usi': subscription.usi})
    return {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
        'course_info': create_course_info(subscription.course),
        'usi': payment_processor.USI_PREFIX + subscription.usi,
        'account_IBAN': conf['IBAN'],
        'account_recipient': conf['recipient'],
        'account_post_number': conf['post_number'] or '-',
        'voucher_url': voucher_url
    }


def send_participation_confirmation(subscription):
    context = _build_subscription_context(subscription)

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
    }

    template = 'online_payment_successful'

    return _email_helper(subscription.user.email, template, context)


def send_sorry_for_incorrect_reminder(subscription):
    context = _build_subscription_context(subscription)

    template = 'sorry_incorrect_payment_reminder'

    return _email_helper(subscription.user.email, template, context)


def send_payment_reminder(subscription):
    context = _build_subscription_context(subscription)

    template = 'payment_reminder'

    return _email_helper(subscription.user.email, template, context)


def send_rejection(subscription, reason):
    context = {
        'first_name': subscription.user.first_name,
        'last_name': subscription.user.last_name,
        'course': subscription.course.type.name,
    }

    template = 'rejection_{}'.format(reason)

    return _email_helper(subscription.user.email, template, context)


def send_teacher_welcome(teach):
    teacher = teach.teacher
    if not teacher.email:
        return None
    course = teach.course

    current_site = Site.objects.get_current().domain
    course_url = current_site + reverse('courses:course_detail', kwargs={'course_id': course.id})
    coursepayment_url = current_site + reverse('payment:coursepayment_detail', kwargs={'course': course.id})
    login_url = current_site + reverse('account_login')
    profile_url = current_site + reverse('edit_profile')

    context = {
        'first_name': teacher.first_name,
        'last_name': teacher.last_name,
        'course': course.type.name,
        'course_internal_name': course.name,
        'course_info': create_course_info(course),
        'room_url': course_url,
        'room_info': course.room.description,
        'room_instructions': course.room.instructions,
        'coursepayment_url': coursepayment_url,
        'login_url': login_url,
        'profile_url': profile_url,
    }

    template = 'teacher_welcome'

    return _email_helper(teacher.email, template, context)


def detect_rejection_reason(subscription):
    """
    detect the reason why the subscription is rejected
    :return: the reason as constant from Rejection.Reason
    """
    reason = courses.models.RejectionReason.UNKNOWN
    counts = subscription.course.get_free_places_count()
    if counts and counts['total'] == 0:
        reason = courses.models.RejectionReason.OVERBOOKED
    elif subscription.course.type.couple_course and subscription.partner is None:
        reason = courses.models.RejectionReason.NO_PARTNER
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
    if course.get_period() and course.offering and course.offering.type == courses.models.OfferingType.REGULAR:
        s += '{}\n'.format(course.get_period())
    if course.format_cancellations():
        s += 'Ausfälle: {}\n'.format(course.format_cancellations())
    if course.format_prices:
        s += 'Kosten: {}\n'.format(course.format_prices())
    return s.strip('\n')
