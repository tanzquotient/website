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
    experience = forms.CharField(required=False)
    general_terms = forms.BooleanField()

    def __init__(self, user: User, course: Course, data: dict = None) -> None:
        super().__init__(data=data)
        self.user = user
        self.course = course

    def clean(self) -> dict:
        cleaned_data = super().clean()
        single_or_couple = cleaned_data.get("single_or_couple")
        partner_email = cleaned_data.get("partner_email")

        # Mandatory experience?
        experience = cleaned_data.get("experience")
        if self.course.experience_mandatory:
            if experience is None or experience.strip() == "":
                error = ValidationError(
                    message=_("This field is required."),
                    code="experience preference empty",
                )
                self.add_error("experience", error)
                return cleaned_data

        # Special validation for couple courses
        if self.course.type.couple_course:
            # Special validation for single subscription to couple course
            if single_or_couple == SingleCouple.SINGLE:
                # Users needs to explicitly specify preference, do not assume "no preference" if "lead_follow" is empty
                if not cleaned_data.get("lead_follow"):
                    error = ValidationError(
                        message=_("This field is required."),
                        code="lead follow preference empty",
                    )
                    self.add_error("lead_follow", error)
                    return cleaned_data

            # Special validation for couple subscription to couple course
            if single_or_couple == SingleCouple.COUPLE:
                # Validation if maximum number is specified
                if self.course.max_subscribers is not None:
                    # At least two spots need to be available
                    # Note: (has_free_places_for_leaders && has_free_places_for_followers) does not
                    #       imply that two spots are available, due to subscribers with no preference
                    if self.course.get_free_places_count() < 2:
                        self.add_error(
                            "partner_email",
                            ValidationError(
                                message=_(
                                    "At least two spots need to be available to sign up as a couple."
                                ),
                                code="not enough free spots for couple",
                            ),
                        )
                        return cleaned_data

                    # At least one spot for leaders needs to be available
                    if not self.course.has_free_places_for_leaders():
                        self.add_error(
                            "partner_email",
                            ValidationError(
                                message=_(
                                    "You can not sign up with a partner anymore, since one of you needs to be the "
                                    "leader and there are no more spots for leaders."
                                ),
                                code="leaders fully booked",
                            ),
                        )
                        return cleaned_data

                    # At least one spot for followers needs to be available
                    if not self.course.has_free_places_for_followers():
                        self.add_error(
                            "partner_email",
                            ValidationError(
                                message=_(
                                    "You can not sign up with a partner anymore, since one of you needs to be the "
                                    "follower and there are no more spots for followers."
                                ),
                                code="leaders fully booked",
                            ),
                        )
                        return cleaned_data

                if not partner_email:
                    error = ValidationError(
                        message=_(
                            "You need to enter the email address of your partner."
                        ),
                        code="partner email missing",
                    )
                    self.add_error("partner_email", error)
                    return cleaned_data

                if not User.objects.filter(email__iexact=partner_email).exists(): # iexact: case insensitive
                    error = ValidationError(
                        message=_(
                            "No user found with this email address. Please make sure your partner has an account"
                        ),
                        code="no user for partner email",
                    )
                    self.add_error("partner_email", error)
                    return cleaned_data

                partner = User.objects.get(email=partner_email)

                if self.user == partner:
                    error = ValidationError(
                        message=_(
                            "You entered yourself as partner! Please enter someone else."
                        ),
                        code="partner equals user",
                    )
                    self.add_error("partner_email", error)
                    return cleaned_data

                if self.course.subscriptions.filter(user=partner).exists():
                    error = ValidationError(
                        message=_("The partner you entered is already signed up."),
                        code="partner already signed up",
                    )
                    self.add_error("partner_email", error)
                    return cleaned_data

                if partner.profile.subscriptions_with_overdue_payment():
                    error = ValidationError(
                        message=_(
                            "The partner you entered has overdue payments "
                            "and can therefore not sign up for any courses."
                        ),
                        code="partner has overdue payments",
                    )
                    self.add_error("partner_email", error)
                    return cleaned_data

        if not cleaned_data.get("lead_follow"):
            cleaned_data["lead_follow"] = LeadFollow.NO_PREFERENCE

        if "comment" in cleaned_data and cleaned_data["comment"].strip() == "":
            del cleaned_data["comment"]

        return cleaned_data
