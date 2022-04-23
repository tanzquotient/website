from datetime import date

from django import forms
from django_countries import countries
from django_countries.fields import LazyTypedChoiceField
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget


from courses.models import StudentStatus, Residence


class UserEditForm(forms.Form):
    first_name = forms.CharField(required=True, label=_("First name"))
    last_name = forms.CharField(required=True, label=_("Last name"))
    phone_number = forms.CharField(max_length=255, required=False)
    phone_number.label = _('Telephone number (Mobile)')
    phone_number.help_text = _('Deine Nummer wird nur für interne Zwecke verwendet und den Lehrern ' 
                               'für das Teilen von Kursinhalten weitergegeben!')
    student_status = forms.BooleanField(required=False, initial=False, label=_('Are you a student?'),
                                        help_text=_('As a student you will profit from reduced course fees'))
    university = forms.ChoiceField(choices=StudentStatus.UNIVERSITY_CHOICES, required=False, label=_('University'))
    gender_options = forms.CharField(required=False, label=_('Gender'))
    gender_custom_value = forms.CharField(required=False)
    body_height = forms.IntegerField(max_value=400, required=False, label=_('Height (cm)'),
                                     help_text=_('Die Körpergrösse (in cm) kann bei Einzelanmeldungen angegeben werden '
                                                 'zum finden eines ähnlich grossen Partners.'))
    legi = forms.CharField(max_length=16, required=False)
    legi.label = _('Student card number')
    newsletter = forms.BooleanField(required=False, initial=True)
    newsletter.label = _('Subscribe to newsletter')
    get_involved = forms.BooleanField(required=False)
    get_involved.label = _('I\'d like to help TQ from time to time (Events etc.)')
    street = forms.CharField(max_length=255, required=False, label=_('Street'))
    plz = forms.IntegerField(required=False, label=_('Postal code'))
    city = forms.CharField(max_length=255, required=False, label=_('City'))
    birthdate = forms.DateField(required=False, widget=forms.widgets.SelectDateWidget(
        empty_label=(_("Choose Year"), _("Choose Month"), _("Choose Day")),
        years=range(date.today().year - 70, date.today().year - 10)))

    picture = forms.ImageField(required=False)
    about_me = forms.CharField(widget=CKEditorWidget, required=False)
    about_me.help_text = _('Tipp: Hier kann auch HTML Code zum Formatieren eingegeben werden!')
    nationality = LazyTypedChoiceField(choices=countries, required=False)
    residence_permit = forms.ChoiceField(choices=Residence.CHOICES, required=False)
    ahv_number = forms.CharField(max_length=255, required=False)
    iban = forms.CharField(max_length=255, required=False)
    bank_name = forms.CharField(max_length=255, required=False)
    bank_zip_code = forms.CharField(max_length=255, required=False)
    bank_city = forms.CharField(max_length=255, required=False)
    bank_country = LazyTypedChoiceField(choices=countries, required=False)

    def clean(self) -> dict:
        cleaned_data = super(UserEditForm, self).clean()

        is_student = cleaned_data.get('student_status', False)

        if is_student:
            if not cleaned_data.get('university'):
                message = _('This field is required if you are a student.')
                self.add_error('university', message)

            if not cleaned_data.get('legi'):
                message = _('This field is required if you are a student.')
                self.add_error('legi', message)

        cleaned_data['student_status'] = cleaned_data.get('university') if is_student else StudentStatus.NO

        cleaned_data['gender'] = cleaned_data.get('gender_options')
        if cleaned_data.get('gender_options') == 'custom':
            cleaned_data['gender'] = cleaned_data.get('gender_custom_value')
        if cleaned_data.get('gender_options') == 'not-specified':
            cleaned_data['gender'] = None

        return cleaned_data
