from django.shortcuts import render

from faq.models import *

# Create your views here.
def faq(request):
    template_name = "faq/faq.html"
    context={}

    context.update({
            'menu': "faq",
            'questions': QuestionGroup.objects.get(name='main_faq').questions.displayed(),
        })
    return render(request, template_name, context)