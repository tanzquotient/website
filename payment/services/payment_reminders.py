from django.db.models import QuerySet
from django.http import HttpRequest

from courses.emailcenter import *
from courses.models import SubscribeState, Subscribe
from ..models import PaymentReminder
from django.contrib import messages
from django.utils.translation import gettext as _
import datetime


def remind_of_payment(
    subscription: Subscribe,
    min_days_from_course_start: int = 0,
    min_days_from_previous_reminder: int = 0,
) -> bool:
    if (
        subscription.state == SubscribeState.CONFIRMED
        and subscription.get_last_payment_reminder()
        > datetime.date.today()
        + datetime.timedelta(days=min_days_from_previous_reminder)
        and subscription.course.has_started_for(
            extra_time=datetime.timedelta(days=min_days_from_course_start)
        )
    ):
        m = send_payment_reminder(subscription)
        if m:
            # log that we sent the reminder
            c = PaymentReminder(subscription=subscription, mail=m)
            c.save()
        return True
    return False


def remind_of_payments(
    subscriptions: QuerySet,
    request: HttpRequest | None = None,
    min_days_from_course_start: int = 0,
    min_days_from_previous_reminder: int = 0,
) -> None:
    sent = 0
    q = subscriptions.filter(state=SubscribeState.CONFIRMED)
    for s in q.all():
        if remind_of_payment(
            s,
            min_days_from_course_start=min_days_from_course_start,
            min_days_from_previous_reminder=min_days_from_previous_reminder,
        ):
            sent += 1
    if request:
        messages.add_message(
            request,
            messages.SUCCESS,
            _("{} of {} reminded successfully").format(sent, subscriptions.count()),
        )


def remind_all_of_payments(
    min_days_from_course_start: int = 0, min_days_from_previous_reminder: int = 0
) -> None:
    remind_of_payments(
        Subscribe.objects.filter(state=SubscribeState.CONFIRMED),
        min_days_from_course_start=min_days_from_course_start,
        min_days_from_previous_reminder=min_days_from_previous_reminder,
    )
