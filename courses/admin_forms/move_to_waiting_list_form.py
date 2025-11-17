from django import forms
from django.utils.translation import gettext_lazy as _


class MoveToWaitingListForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    send_email = forms.BooleanField(
        required=False,
        label=_("Notify via email?"),
        help_text=_(
            "Whether the user(s) should be informed "
            "that they have been moved to the waiting "
            "list via email."
        ),
        initial=False,
    )
