from django import forms

from models import GENDER
from models import STUDENT_STATUS
from courses.models import STUDENT_STATUS

class UserForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    first_name.label = u'Vorname'
    last_name = forms.CharField(max_length=100)
    last_name.label = u'Nachname'
    gender = forms.ChoiceField(choices=GENDER)
    gender.label = u'Geschlecht'
    street = forms.CharField(max_length=100)
    street.label = u'Strasse'
    plz = forms.IntegerField()
    plz.label = u'PLZ'
    city = forms.CharField(max_length=100)
    city.label = u'Ort'
    phone_number = forms.CharField(max_length=100, required=False)
    phone_number.label = u'Telefonnummer (Mobile)'
    email = forms.EmailField()
    email.label = u'E-Mail'
    email_repetition = forms.EmailField()
    email_repetition.label = u'E-Mail Wiederholung'
    student_status = forms.ChoiceField(choices=STUDENT_STATUS)
    student_status.label = u'Student'
    legi = forms.CharField(max_length=100, required=False)
    legi.label = u'Legi-Nummer'
    experience = forms.CharField(widget=forms.Textarea, required=False)
    experience.label = u'Erfahrung'
    comment = forms.CharField(widget=forms.Textarea, required=False)
    comment.label = u'Kommentar'
    newsletter = forms.BooleanField(required=False)
    newsletter.label = u'Newsletter abonnieren'
    
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        email = cleaned_data.get("email")
        email_repetition = cleaned_data.get("email_repetition")

        if email != email_repetition:
            msg=u"Email-Adressen sind nicht gleich."
            self.add_error('email_repetition', msg)
            raise forms.ValidationError(msg)

        # if a student, the legi must be set
        if cleaned_data.get('student_status') != 'no' and not cleaned_data.get('legi'):
            msg=u"Legi muss fuer Studenten angegeben werden."
            self.add_error('legi', msg)
            raise forms.ValidationError(msg)
            