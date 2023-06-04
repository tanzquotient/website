from django import forms
from django.utils.translation import gettext as _

from courses.models import *


class RejectForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    reason = forms.ChoiceField(
        label=_("Select Reason"), choices=RejectionReason.CHOICES
    )
    send_email = forms.BooleanField(
        label=_("Inform subscriber about cancellation"), required=False
    )
