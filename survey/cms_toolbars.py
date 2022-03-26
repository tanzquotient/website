from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar


@toolbar_pool.register
class SurveyToolbar(CMSToolbar):
    def populate(self) -> None:
        menu = self.toolbar.get_or_create_menu('survey-app', _('Survey'))
        if self.request.user.has_perm('survey.change_survey'):
            url = reverse('admin:survey_survey_changelist')
            menu.add_sideframe_item(_('Surveys'), url=url)
        if self.request.user.has_perm('survey.change_questiongroup'):
            url = reverse('admin:survey_questiongroup_changelist')
            menu.add_sideframe_item(_('Question groups'), url=url)
        if self.request.user.has_perm('survey.change_question'):
            url = reverse('admin:survey_question_changelist')
            menu.add_sideframe_item(_('Questions'), url=url)
        if self.request.user.has_perm('survey.change_scale'):
            url = reverse('admin:survey_scale_changelist')
            menu.add_sideframe_item(_('Templates for scale questions'), url=url)
        if self.request.user.has_perm('survey.change_Choice'):
            url = reverse('admin:survey_choice_changelist')
            menu.add_sideframe_item(_('Choices'), url=url)

        menu.add_break('reference-operational-break')

        if self.request.user.has_perm('survey.change_answer'):
            url = reverse('admin:survey_answer_changelist')
            menu.add_sideframe_item(_('Answers'), url=url)
        if self.request.user.has_perm('survey.change_survey'):
            url = reverse('admin:survey_surveyinstance_changelist')
            menu.add_sideframe_item(_('Survey Instances'), url=url)
