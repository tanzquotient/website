from datetime import date

from django import forms
from django_countries import countries
from django_countries.fields import LazyTypedChoiceField
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget


from courses.models import StudentStatus, Gender, Residence


class UserEditForm(forms.Form):
    phone_number = forms.CharField(max_length=255, required=False)
    phone_number.label = _('Telephone number (Mobile)')
    phone_number.help_text = _('Deine Nummer wird nur für interne Zwecke verwendet und den Lehrern ' 
                             'für das Teilen von Kursinhalten weitergegeben!')
    student_status = forms.ChoiceField(choices=StudentStatus.CHOICES)
    student_status.label = _('Student')
    gender = forms.ChoiceField(choices=Gender.CHOICES)
    gender.label = _('Gender')
    body_height = forms.IntegerField(max_value=400, required=False)
    body_height.label = _('Height (cm)')
    body_height.help_text = _('Die Körpergrösse (in cm) kann bei Einzelanmeldungen angegeben werden '
                              'zum finden eines ähnlich grossen Partners.')
    legi = forms.CharField(max_length=16, required=False)
    legi.label = _('Student card number')
    newsletter = forms.BooleanField(required=False, initial=True)
    newsletter.label = _('Subscribe to newsletter')
    get_involved = forms.BooleanField(required=False)
    get_involved.label = _('I\'d like to help TQ from time to time (Events etc.)')
    street = forms.CharField(max_length=255)
    street.label = _('Street')
    plz = forms.IntegerField()
    plz.label = _('Postal code')
    city = forms.CharField(max_length=255)
    city.label = _('City')
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


def clean(self):
    cleaned_data = super(UserEditForm, self).clean()

    # if a student, the legi must be set
    if cleaned_data.get('student_status') != 'no' and not cleaned_data.get('legi'):
        msg = _("Students have to enter their student card number.")
        self.add_error('legi', msg)
        raise forms.ValidationError(msg)

    return cleaned_data
