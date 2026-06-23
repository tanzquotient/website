from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from . import VoucherForm


class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.get_full_name()} ({obj.username}) — {obj.email}"


class VoucherGenerationForm(VoucherForm):
    custom_email_message_en = None
    custom_email_message_de = None

    number_of_vouchers = forms.IntegerField(
        label=_("How many vouchers should be generated?"), initial=20
    )
    recipients = UserMultipleChoiceField(
        label=_("Recipients (optional)"),
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("users", is_stacked=False),
        help_text=_(
            "If set, each voucher will be assigned to one recipient. Count must equal number of vouchers."
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        recipients = cleaned_data.get("recipients")
        n = cleaned_data.get("number_of_vouchers")
        if recipients and n is not None and len(recipients) != n:
            raise forms.ValidationError(
                _(
                    f"Number of recipients ({len(recipients)}) must match number of vouchers ({n})."
                )
            )
        return cleaned_data
