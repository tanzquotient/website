from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _
from django_countries.data import COUNTRIES
from django_countries.fields import LazyTypedChoiceField
from djangocms_text.widgets import TextEditorWidget

from courses.models import StudentStatus, Residence, UserProfile
from utils.iban_validator import validate_iban


class UserEditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(UserEditForm, self).__init__(*args, **kwargs)

    first_name = forms.CharField(required=True, label=_("First name"))
    last_name = forms.CharField(required=True, label=_("Last name"))
    display_name = forms.CharField(
        required=False, max_length=30, label=_("Display name")
    )
    phone_number = forms.CharField(max_length=255, required=False)
    phone_number.label = _("Telephone number (mobile)")
    phone_number.help_text = _(
        "Your phone number is used for internal purposes and may be shared "
        "with teachers and, for couple courses, with your assigned partner. "
        "You may opt out of sharing with your partner using the option below."
    )
    student_status = forms.BooleanField(
        required=False,
        initial=False,
        label=_("Are you a student?"),
        help_text=_("As a student you will profit from reduced course fees"),
    )
    university = forms.ChoiceField(
        choices=StudentStatus.UNIVERSITY_CHOICES, required=False, label=_("University")
    )
    gender_options = forms.CharField(required=False, label=_("Gender"))
    gender_custom_value = forms.CharField(required=False)
    body_height = forms.IntegerField(
        max_value=400,
        required=False,
        label=_("Height (cm)"),
        help_text=_(
            "Die Körpergrösse (in cm) kann bei Einzelanmeldungen angegeben werden "
            "zum finden eines ähnlich grossen Partners."
        ),
    )
    legi = forms.CharField(max_length=16, required=False)
    legi.label = _("Student card number")
    newsletter = forms.BooleanField(required=False, initial=True)
    newsletter.label = _("Subscribe to newsletter")
    get_involved = forms.BooleanField(required=False)
    get_involved.label = _(
        "I'd like to help Tanzquotient from time to time (Events etc.)"
    )
    personal_data_sharing = forms.BooleanField(required=False)
    personal_data_sharing.label = _(
        "Share personal data with partner in couple courses"
    )
    personal_data_sharing.help_text = _(
        "If you agree, your full name, phone number (if provided) and "
        "email address will be shared with your partner in couple courses. "
        "Otherwise, only your first name and initial of "
        "your last name will be shared."
    )
    street = forms.CharField(max_length=255, required=False, label=_("Street"))
    plz = forms.IntegerField(required=False, label=_("Postal code"))
    city = forms.CharField(max_length=255, required=False, label=_("City"))
    birthdate = forms.DateField(
        required=False,
        widget=forms.widgets.SelectDateWidget(
            empty_label=(_("Choose Year"), _("Choose Month"), _("Choose Day")),
            years=range(date.today().year - 70, date.today().year - 10),
        ),
    )

    picture = forms.ImageField(required=False)
    picture.help_text = _(
        "This image will be center cropped and rescaled to 512x512px upon upload."
    )
    about_me = forms.CharField(widget=TextEditorWidget, required=False)
    about_me.help_text = _(
        "Tipp: Hier kann auch HTML Code zum Formatieren eingegeben werden!"
    )
    nationality = LazyTypedChoiceField(
        choices=[("", _("Select country"))] + list(COUNTRIES.items()), required=False
    )
    residence_permit = forms.ChoiceField(choices=Residence.CHOICES, required=False)
    ahv_number = forms.CharField(max_length=255, required=False)
    zemis_number = forms.CharField(max_length=255, required=False)
    iban = forms.CharField(max_length=255, required=False, validators=[validate_iban])
    bank_name = forms.CharField(max_length=255, required=False)
    bank_zip_code = forms.CharField(max_length=255, required=False)
    bank_city = forms.CharField(max_length=255, required=False)
    bank_country = LazyTypedChoiceField(
        choices=[("", _("Select country"))] + list(COUNTRIES.items()), required=False
    )

    def clean(self) -> dict:
        cleaned_data = super(UserEditForm, self).clean()

        if (
            cleaned_data.get("display_name")
            and UserProfile.objects.exclude(user=self.user)
            .filter(display_name=cleaned_data.get("display_name"))
            .exists()
        ):
            message = _(
                "This display name is already in use. Please choose a different one."
            )
            self.add_error("display_name", message)

        is_student = cleaned_data.get("student_status", False)

        if is_student:
            if not cleaned_data.get("university"):
                message = _("This field is required if you are a student.")
                self.add_error("university", message)

            if not cleaned_data.get("legi"):
                message = _("This field is required if you are a student.")
                self.add_error("legi", message)

        cleaned_data["student_status"] = (
            cleaned_data.get("university") if is_student else StudentStatus.NO
        )

        cleaned_data["gender"] = cleaned_data.get("gender_options")
        if cleaned_data.get("gender_options") == "custom":
            cleaned_data["gender"] = cleaned_data.get("gender_custom_value")
        if cleaned_data.get("gender_options") == "not-specified":
            cleaned_data["gender"] = None

        return cleaned_data
