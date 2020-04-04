from django import forms

from courses.forms import SingleSubscriptionForm


class CoupleSubscriptionForm(SingleSubscriptionForm):

    partner_email = forms.EmailField(required=False)
