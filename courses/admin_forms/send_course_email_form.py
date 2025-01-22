from django import forms
from django.utils.translation import gettext_lazy as _
from djangocms_text.widgets import TextEditorWidget
from post_office.models import EmailTemplate


from survey.models import Survey
from courses.models.choices import SubscribeState


class SendCourseEmailForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    email_template = forms.ModelChoiceField(
        label=_("Email template"),
        help_text=_("Can be left empty if Subject and Content are specified."),
        queryset=EmailTemplate.objects.all(),
        required=False,
    )
    email_subject = forms.CharField(
        label=_("Subject"),
        help_text=_("If left empty, uses subject of template."),
        required=False,
    )
    email_content = forms.CharField(
        label=_("Content"),
        help_text=_("Compose your own text. Email template will not be used.")
        + " "
        + _("You can use the following placeholders:")
        + " "
        + "first_name, last_name, course, offering, survey_url, survey_expiration",
        required=False,
        widget=TextEditorWidget,
    )

    send_to_participants = forms.BooleanField(
        label=_("Send to Participants"),
        required=False,
        initial=True,
    )

    subscribe_state = forms.MultipleChoiceField(
        choices=SubscribeState.CHOICES,
        required=False,
        label=_(
            "Select the subscription state of participants that should receive the email:"
        ),
        widget=forms.CheckboxSelectMultiple,
        initial=SubscribeState.ACCEPTED_STATES,
    )

    send_to_teachers = forms.BooleanField(
        label=_("Send to Teachers"),
        required=False,
        initial=True,
    )

    survey = forms.ModelChoiceField(
        label=_("Optional: Select Survey"),
        help_text=_("If specified, you can use the 'survey_url' placeholder."),
        queryset=Survey.objects.all(),
        required=False,
    )

    survey_url_expire_date = forms.DateTimeField(
        label=_("Optional: Expiration date for survey"),
        help_text=_("Surveys will not expire if left empty."),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        email_content = cleaned_data.get("email_content")
        email_subject = cleaned_data.get("email_subject")
        email_template = cleaned_data.get("email_template")

        if not email_template:
            if not email_subject:
                raise forms.ValidationError(
                    _(
                        "Subject not specified. Please specify either a template or enter the subject directly!"
                    ),
                    "No subject",
                )
            if not email_content:
                raise forms.ValidationError(
                    _(
                        "Content not specified. Please specify either a template or enter the content directly!"
                    ),
                    "No content",
                )
