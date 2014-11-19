from django.shortcuts import render

from faq.models import *

# Create your views here.
def faq(request):
    template_name = "faq/faq.html"
    context={}

    context.update({
            'menu': "faq",
            'questions': Question.objects.displayed(),
        })
    return render(request, template_name, context)