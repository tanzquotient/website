from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Model, DateTimeField, BooleanField, ForeignKey, PROTECT, SET_NULL
from django.urls import reverse
from django.utils.encoding import escape_uri_path
from post_office.models import EmailTemplate

from survey.services import encode_id


class SurveyInstance(Model):
    survey = ForeignKey('Survey', related_name='survey_instances', blank=False, null=False, on_delete=PROTECT)
    email_template = ForeignKey(EmailTemplate, related_name='survey_instances', blank=True, null=True,
                                on_delete=SET_NULL)
    user = ForeignKey(User, related_name='survey_instances', blank=False, null=False, on_delete=PROTECT)
    course = ForeignKey('courses.Course', related_name='survey_instances', blank=True, null=True, on_delete=PROTECT)
    date = DateTimeField(blank=False, null=False, auto_now_add=True)
    last_update = DateTimeField(blank=True, null=True, auto_now=True)
    url_expire_date = DateTimeField(blank=True, null=True)
    invitation_sent = BooleanField(default=False)

    def get_url(self) -> str:
        return self.create_url()

    def create_url(self) -> str:
        id_str, c = encode_id(self.id)
        return f"{reverse('survey:survey_invitation')}?id={escape_uri_path(id_str)}&c={escape_uri_path(c)}"

    def create_full_url(self) -> str:
        return f"https://{settings.DEPLOYMENT_DOMAIN}{self.create_url()}"

    def __str__(self) -> str:
        if self.course:
            return "{} for {} of {}".format(self.survey, self.course, self.user)
        else:
            return "{} of {}".format(self.survey, self.user)
