from django.http import Http404
from django.shortcuts import render, redirect
import services
import models
from django.shortcuts import get_object_or_404
import re
import logging

log = logging.getLogger('tq')


# Create your views here.

def survey_invitation(request):
    # clear session keys

    # if this is a POST request we need to process the form data
    if request.method == 'POST' and 'send' in request.POST:
        log.info(request.POST)
        if 'inst_id' not in request.session:
            raise Http404()
        inst_id = request.session['inst_id']
        del request.session['inst_id']
        survey_instance = get_object_or_404(models.SurveyInstance, pk=inst_id)

        prog = re.compile(r'^q(?P<question>\d+)-c?(?P<choice>\S+)$')
        errors = 0
        for key, value in request.POST.iteritems():
            m = prog.match(key)
            q = m.group('question')
            c = m.group('choice')
            if not q or not c:
                continue
            question = models.Question.objects.get(pk=int(q))
            if not question:
                errors += 1
                continue
            a = models.Answer.create(survey_instance, c, request.POST[key])
            log.info(a)

        if errors:
            log.error("we could not process {} of the keys in POST".format(errors))

        for group in survey_instance.survey.questiongroup_set.all():
            for question in group.question_set.all():

                if question.type == models.Question.Type.FREE_FORM:
                    for choice in question.choice_set.all():
                        v = request.POST.get("q-{}-text-{}".format(question.id, choice.id), "")

                    if "q-{}-text-default".format(question.id) in request.POST:
                        pass

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

            intro_text = survey_instance.survey.intro_text
            intro_text = re.sub(r"\{\{\s*name\s*\}\}", survey_instance.user.first_name, intro_text)
            intro_text = re.sub(r"\{\{\s*course\s*\}\}", survey_instance.course,
                                intro_text)
            # TODO: currently only teachers of first course are shown (replaced where {{ teacher }}-tag appears)
            intro_text = re.sub(r"\{\{\s*teachers\s*\}\}", survey_instance.course.format_teachers(),
                                intro_text)
        else:
            raise Http404("no GET arguments supplied: do not know which survey instance to load")

        context = {'inst': survey_instance,
                   'intro_text': intro_text}

        return render(request, template_name, context)


def survey_done(request):
    template_name = "survey/survey_done.html"
    return render(request, template_name, {})


def survey_test(request, survey_id):
    template_name = "survey/survey.html"

    survey = get_object_or_404(models.Survey, pk=survey_id)
    context = {'inst': models.SurveyInstance(survey=survey),
               'intro_text': survey.intro_text}

    return render(request, template_name, context)
