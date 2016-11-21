from courses.emailcenter import *
from courses.models import Subscribe
from .models import PaymentReminder
from django.contrib import messages
from django.utils.translation import ugettext as _
import datetime


def remind_of_payment(subscription):
    if subscription.state == Subscribe.State.CONFIRMED and subscription.get_last_payment_reminder() != datetime.date.today():
        m = send_payment_reminder(subscription)
        if m:
            # log that we sent the reminder
            c = PaymentReminder(subscription=subscription, mail=m)
            c.save()
        return True
    return False


def remind_of_payments(subscriptions, request):
    sent = 0
    q = subscriptions.filter(state=Subscribe.State.CONFIRMED)
    for s in q.all():
        if remind_of_payment(s):
            sent += 1
    messages.add_message(request, messages.SUCCESS,
                         _(u'{} of {} reminded successfully').format(sent, subscriptions.count()))
