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

        # If this course is couples-only, require coupling
        if self.course.partner_required_at_signup:
            if single_or_couple != SingleCouple.COUPLE:
                error = ValidationError(
                    message=_("You must sign up together with a partner."),
                    code="partner required",
                )
                self.add_error("single_or_couple", error)
                return cleaned_data

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
            # Users needs to explicitly specify preference, do not assume "no preference" if "lead_follow" is empty
            if not cleaned_data.get(f"lead_follow"):
                error = ValidationError(
                    message=_("This field is required."),
                    code="lead follow preference empty",
                )
                self.add_error(f"lead_follow", error)
                return cleaned_data

            # Special validation for couple subscription to couple course
            if single_or_couple == SingleCouple.COUPLE:

                if not partner_email:
                    error = ValidationError(
                        message=_(
                            "You need to enter the email address of your partner."
                        ),
                        code="partner email missing",
                    )
                    self.add_error("partner_email", error)
                    return cleaned_data

                if not User.objects.filter(
                    email__iexact=partner_email
                ).exists():  # iexact: case insensitive
                    error = ValidationError(
                        message=_(
                            "No user found with this email address. Please make sure your partner has an account"
                        ),
                        code="no user for partner email",
                    )
                    self.add_error("partner_email", error)
                    return cleaned_data

                partner = User.objects.filter(email=partner_email).first()
                if (
                    partner is None
                    and User.objects.filter(email__iexact=partner_email).count() > 1
                ):
                    error = ValidationError(
                        message=_(
                            "Please check the upper/lower casing of this email address."
                        ),
                        code="multiple users for partner email",
                    )
                    self.add_error("partner_email", error)
                    return cleaned_data
                elif partner is None:
                    partner = User.objects.get(email__iexact=partner_email)

                if self.user == partner:
                    error = ValidationError(
                        message=_(
                            "You entered yourself as partner! Please enter someone else."
                        ),
                        code="partner equals user",
                    )
                    self.add_error("partner_email", error)
                    return cleaned_data

                if not self.course.user_can_subscribe(partner, self.user.is_staff):
                    error = ValidationError(
                        message=_(
                            "The partner you entered is already signed up or cannot subscribe to this course."
                        ),
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
