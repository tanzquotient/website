from django.http import Http404
from django.shortcuts import render
import services
import models
from django.shortcuts import get_object_or_404
import re
from models import SurveyInstance


# Create your views here.

def survey_invitation(request):
    template_name = "survey/survey.html"

    if 't' in request.GET and 'c' in request.GET:
        text = request.GET['t']
        checksum = request.GET['c']
        survey_instance_id = services.decode_data(text, checksum)
        survey_instance = get_object_or_404(models.SurveyInstance, pk=survey_instance_id)

        intro_text = survey_instance.survey.intro_text
        intro_text = re.sub(r"\{\{\s*name\s*\}\}", survey_instance.user.first_name, intro_text)
        intro_text = re.sub(r"\{\{\s*courses\s*\}\}", ",".join(map(str, survey_instance.courses.all())), intro_text)
        # TODO: currently only teachers of first course are shown (replaced where {{ teacher }}-tag appears)
        intro_text = re.sub(r"\{\{\s*teachers\s*\}\}", survey_instance.courses.first().format_teachers(), intro_text)
    else:
        raise Http404("no args suplied")

    context = {'inst': survey_instance,
               'intro_text': intro_text}

    return render(request, template_name, context)

def survey_test(request, survey_id):
    template_name = "survey/survey.html"

    survey = get_object_or_404(models.Survey, pk=survey_id)
    context = {'inst': SurveyInstance(survey=survey),
               'intro_text': survey.intro_text}

    return render(request, template_name, context)
