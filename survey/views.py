from django.utils import timezone
from django.http import Http404
from django.shortcuts import render, redirect
import services
import models
from django.shortcuts import get_object_or_404
import re
import logging
from django.utils.translation import ugettext as _

log = logging.getLogger('tq')


# Create your views here.

def survey_invitation(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST' and 'send' in request.POST:
        if 'inst_id' not in request.session:
            raise Http404()
        inst_id = request.session['inst_id']
        del request.session['inst_id']
        survey_instance = get_object_or_404(models.SurveyInstance, pk=inst_id)

        prog = re.compile(r'^q(?P<question>\d+)-?c?(?P<choice>\S+)?$')
        for key, value in request.POST.iteritems():
            if not key:
                log.debug(u"ignore {}".format(key))
                continue
            m = prog.match(key)
            if not m:
                log.debug(u"no match {}".format(key))
                continue
            q = m.group('question')
            c = m.group('choice')
            if not q:
                log.debug(u"question could not be parsed in {}".format(key))
                continue

            question = get_object_or_404(models.Question, pk=int(q))
            try:
                if question.type in [models.Question.Type.SINGLE_CHOICE,
                                     models.Question.Type.SINGLE_CHOICE_WITH_FREE_FORM]:
                    if c=='freechoice':
                        continue
                    if c:
                        a = models.Answer.create(survey_instance, question, c, value)
                    else:
                        a = models.Answer.create(survey_instance, question, int(value))
                else:
                    if not c:
                        log.error("Fatal programming error: answer of survey not in correct format")
                        continue
                    if c == 'freechoice':
                        # ignore
                        continue
                    a = models.Answer.create(survey_instance, question, c, value)
                a.save()
            except Exception as e:
                log.error("Fatal programming error: {}".format(e.message))

        survey_instance.last_update = timezone.now()
        survey_instance.save()

        return redirect('survey:survey_done')
    # if a GET (or any other method) we'll create a blank form
    else:
        if 'inst_id' in request.session:
            del request.session['inst_id']

        template_name = "survey/survey.html"
        if 't' in request.GET:
            # old format: for backwards compatibility, show a message to user
            request.session['msg'] = _("This survey link has expired (format has changed)")
            return redirect('survey:survey_error')
        if 'id' in request.GET and 'c' in request.GET:
            id_str = request.GET['id']
            c = request.GET['c']
            inst_id = services.decode_id(id_str, c)
            if not inst_id:
                request.session['msg'] = _("There is a technical problem with your link. We are very sorry. Please inform us on informatik@tq.vseth.ch WITH YOUR FULL NAME if you still want to take part in the survey")
                return redirect('survey:survey_error')
            log.debug( inst_id)
            survey_instance = get_object_or_404(models.SurveyInstance, pk=inst_id)

            request.session['inst_id'] = inst_id

            # check if survey was already filled out -> show error message
            if survey_instance.last_update is not None:
                request.session['msg'] = _("This survey was already filled out")
                return redirect('survey:survey_error')
            if survey_instance.url_expire_date is not None and survey_instance.url_expire_date <= timezone.now():
                request.session['msg'] = _("This survey link has expired")
                return redirect('survey:survey_error')

            intro_text = survey_instance.survey.intro_text or ""
            intro_text = re.sub(r"\{\{\s*name\s*\}\}", survey_instance.user.first_name, intro_text)
            intro_text = re.sub(r"\{\{\s*course\s*\}\}", str(survey_instance.course) or "",
                                intro_text)
            intro_text = re.sub(r"\{\{\s*teachers\s*\}\}",
                                survey_instance.course.format_teachers() if survey_instance.course else "",
                                intro_text)
        else:
            raise Http404("no GET arguments supplied: do not know which survey instance to load")

        context = {'inst': survey_instance,
                   'intro_text': intro_text}

        return render(request, template_name, context)


def survey_done(request):
    template_name = "survey/survey_done.html"
    return render(request, template_name, {})


def survey_error(request):
    template_name = "survey/survey_error.html"

    message = request.session.get('msg', _("Error"))

    return render(request, template_name, {'message': message})


def survey_test(request, survey_id):
    template_name = "survey/survey.html"

    survey = get_object_or_404(models.Survey, pk=survey_id)
    context = {'inst': models.SurveyInstance(survey=survey),
               'intro_text': survey.intro_text}

    return render(request, template_name, context)
