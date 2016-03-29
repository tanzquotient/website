from django.shortcuts import render
import services
import models
from django.shortcuts import get_object_or_404

# Create your views here.

def survey_invitation(request):
    template_name = "survey.html"
    text = request.GET['t']
    checksum = request.GET['c']
    survey_instance_id = services.decode_data(text, checksum)
    survey_instance = get_object_or_404(models.SurveyInstance, pk=survey_instance_id)
    context = {'inst': survey_instance}

    return render(request, template_name, context)
