from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from courses.models import LeadFollow, SingleCouple, Course


class SubscribeForm(forms.Form):
    single_or_couple = forms.ChoiceField(choices=SingleCouple.CHOICES, required=True)
    lead_follow = forms.ChoiceField(choices=LeadFollow.CHOICES, required=False)
    partner_email = forms.EmailField(required=False)
    comment = forms.CharField(required=False)
    general_terms = forms.BooleanField()

    def __init__(self, user: User, course: Course, data: dict = None) -> None:
        super().__init__(data=data)
        self.user = user
        self.course = course

    def clean(self) -> dict:
        cleaned_data = super().clean()
        single_or_couple = cleaned_data.get("single_or_couple")
        partner_email = cleaned_data.get("partner_email")

        if not cleaned_data.get("lead_follow"):
            cleaned_data["lead_follow"] = LeadFollow.NO_PREFERENCE

        if "comment" in cleaned_data and cleaned_data["comment"].strip() == '':
            del cleaned_data["comment"]

        if single_or_couple == SingleCouple.COUPLE:

            if not self.course.has_free_places_for_leaders():
                error = ValidationError(
                    message=_('You can not sign up with a partner anymore, '
                              'since one of you needs to be the leader and there are no more spots for leaders.'),
                    code='leaders fully booked')
                self.add_error('partner_email', error)
                return cleaned_data

            if not self.course.has_free_places_for_followers():
                error = ValidationError(
                    message=_('You can not sign up with a partner anymore, '
                              'since one of you needs to be the follower and there are no more spots for followers.'),
                    code='leaders fully booked')
                self.add_error('partner_email', error)
                return cleaned_data

            if not partner_email:
                error = ValidationError(
                    message=_('You need to enter the email address of your partner.'),
                    code='partner email missing')
                self.add_error('partner_email', error)
                return cleaned_data

            if not User.objects.filter(email=partner_email).exists():
                error = ValidationError(
                    message=_('No user found with this email address. Please make sure your partner has an account'),
                    code='no user for partner email')
                self.add_error('partner_email', error)
                return cleaned_data

            partner = User.objects.get(email=partner_email)

            if self.user == partner:
                error = ValidationError(
                    message=_('You entered yourself as partner! Please enter someone else.'),
                    code='partner equals user'
                )
                self.add_error('partner_email', error)
                return cleaned_data

            if self.course.subscriptions.filter(user=partner).exists():
                error = ValidationError(
                    message=_('The partner you entered is already signed up.'),
                    code='partner already signed up'
                )
                self.add_error('partner_email', error)
                return cleaned_data

            if partner.profile.subscriptions_with_overdue_payment():
                error = ValidationError(
                    message=_('The partner you entered has overdue payments '
                              'and can therefore not sign up for any courses.'),
                    code='partner has overdue payments'
                )
                self.add_error('partner_email', error)
                return cleaned_data

        return cleaned_data




