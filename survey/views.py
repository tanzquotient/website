import datetime
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

        prog = re.compile(r'^q(?P<question>\d+)-c?(?P<choice>\S+)$')
        for key, value in request.POST.iteritems():
            if not key:
                continue
            m = prog.match(key)
            if not m:
                continue
            q = m.group('question')
            c = m.group('choice')
            if not q or not c:
                continue
            a = models.Answer.create(survey_instance, q, c, request.POST[key])
            a.save()

        survey_instance.last_update = datetime.datetime.now()
        survey_instance.save()

        return redirect('survey:survey_done')
    # if a GET (or any other method) we'll create a blank form
    else:
        if 'inst_id' in request.session:
            del request.session['inst_id']

        template_name = "survey/survey.html"
        if 't' in request.GET and 'c' in request.GET:
            text = request.GET['t']
            checksum = request.GET['c']
            survey_instance_id = services.decode_data(text, checksum)
            survey_instance = get_object_or_404(models.SurveyInstance, pk=survey_instance_id)

            request.session['inst_id'] = survey_instance_id

            # check if survey was already filled out -> show error message
            if survey_instance.last_update is not None:
                request.session['msg'] = _("This survey was already filled out")
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
    inst_id = request.session.get('inst_id')
    survey_inst = get_object_or_404(models.SurveyInstance, pk=inst_id)

    return render(request, template_name, {'message': message, 'inst': survey_inst})


def survey_test(request, survey_id):
    template_name = "survey/survey.html"

    survey = get_object_or_404(models.Survey, pk=survey_id)
    context = {'inst': models.SurveyInstance(survey=survey),
               'intro_text': survey.intro_text}

    return render(request, template_name, context)
