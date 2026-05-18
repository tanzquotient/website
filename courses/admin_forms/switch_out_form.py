from django import forms
from django.utils.translation import gettext as _

from courses.models import RejectionReason


class SwitchOutForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    reason = forms.ChoiceField(
        label=_("Rejection reason for outgoing person"),
        choices=RejectionReason.CHOICES,
    )
    send_email = forms.BooleanField(
        label=_("Inform outgoing person about rejection"),
        initial=True,
        required=False,
    )
