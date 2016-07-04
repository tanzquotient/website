from django import forms

from .models import UserProfile


class UserForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    first_name.label ='Vorname'
    last_name = forms.CharField(max_length=30)
    last_name.label ='Nachname'
    gender = forms.ChoiceField(choices=UserProfile.Gender.CHOICES)
    gender.label ='Geschlecht'
    street = forms.CharField(max_length=255)
    street.label ='Strasse'
    plz = forms.IntegerField()
    plz.label ='PLZ'
    city = forms.CharField(max_length=255)
    city.label ='Ort'
    phone_number = forms.CharField(max_length=255, required=False)
    phone_number.label ='Telefonnummer (Mobile)'
    email = forms.EmailField(max_length=75)
    email.label ='E-Mail'
    email_repetition = forms.EmailField(max_length=75)
    email_repetition.label ='E-Mail Wiederholung'
    student_status = forms.ChoiceField(choices=UserProfile.StudentStatus.CHOICES)
    student_status.label ='Student'
    legi = forms.CharField(max_length=16, required=False)
    legi.label ='Legi-Nummer'
    body_height = forms.IntegerField(max_value=400, required=False)
    body_height.label ='Körpergrösse (cm)'
    body_height.help_text ='Die Körpergrösse (in cm) kann bei Einzelanmeldungen angegeben werden zum finden eines ähnlich grossen Partners.'
    experience = forms.CharField(widget=forms.Textarea, max_length=1000, required=False)
    experience.label ='Erfahrung'
    comment = forms.CharField(widget=forms.Textarea, max_length=1000, required=False)
    comment.label ='Kommentar'
    newsletter = forms.BooleanField(required=False)
    newsletter.label ='Newsletter abonnieren'
    get_involved = forms.BooleanField(required=False)
    get_involved.label ='Ich würde gerne ab und zu beim TQ mithelfen (Events etc.)'

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        email = cleaned_data.get("email")
        email_repetition = cleaned_data.get("email_repetition")

        if email != email_repetition:
            msg ="Email-Adressen sind nicht gleich."
            self.add_error('email_repetition', msg)
            raise forms.ValidationError(msg)

        # if a student, the legi must be set
        if cleaned_data.get('student_status') != 'no' and not cleaned_data.get('legi'):
            msg ="Legi muss fuer Studenten angegeben werden."
            self.add_error('legi', msg)
            raise forms.ValidationError(msg)
