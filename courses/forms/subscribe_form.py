from django import forms

from courses.models import LeadFollow


class SubscribeForm(forms.Form):
    single_or_couple = forms.ChoiceField(choices=("single", "couple"), required=True)
    lead_follow = forms.ChoiceField(choices=LeadFollow.CHOICES, required=False)
    partner_email = forms.EmailField(required=False)
    comment = forms.CharField(max_length=1000, required=False)
    general_terms = forms.BooleanField(required=True)
