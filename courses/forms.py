from django import forms

from models import GENDER
from models import STUDENT_STATUS

class UserForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    gender = forms.ChoiceField(choices=GENDER)
    street = forms.CharField(max_length=100)
    plz = forms.IntegerField()
    city = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=100, required=False)
    email = forms.EmailField()
    email_repetition = forms.EmailField()
    student_status = forms.ChoiceField(choices=STUDENT_STATUS)
    legi = forms.CharField(max_length=100, required=False)
    experience = forms.CharField(widget=forms.Textarea, required=False)
    comment = forms.CharField(widget=forms.Textarea, required=False)
    newsletter = forms.BooleanField(required=True)
    
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        email = cleaned_data.get("email")
        email_repetition = cleaned_data.get("email_repetition")

        if email != email_repetition:
            msg="Email adresses do not match."
            self.add_error('email_repetition', msg)
            raise forms.ValidationError(msg)

        # if a student, the legi must be set
        if cleaned_data.get('student_status') != 'no' and not cleaned_data.get('legi'):
            msg="Legi must be set for students."
            self.add_error('legi', msg)
            raise forms.ValidationError(msg)
            