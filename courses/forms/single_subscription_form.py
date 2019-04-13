from django import forms


class SingleSubscriptionForm(forms.Form):
    textarea_attribs = {'rows': '4', 'cols': '80'}
    experience = forms.CharField(widget=forms.Textarea(textarea_attribs), max_length=1000, required=False)
    experience.label = 'Erfahrung'
    comment = forms.CharField(widget=forms.Textarea(textarea_attribs), max_length=1000, required=False)
    comment.label = 'Kommentar'

    general_terms = forms.BooleanField(required=True)
    general_terms.label = 'I/We accept that the enrollment is binding.'
