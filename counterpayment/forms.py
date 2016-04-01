from django import forms

class USIForm(forms.Form):
    usi = forms.CharField(max_length=6, label="Unique Course Identifier (USI)")