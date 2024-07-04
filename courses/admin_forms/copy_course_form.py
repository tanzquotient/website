from django import forms
from django.utils.translation import gettext as _

from courses.models import *


class CopyCourseForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    offering = forms.ModelChoiceField(
        queryset=Offering.objects.all(), label=_("Offering to copy into")
    )
