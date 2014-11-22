from django.shortcuts import render
from organisation.models import Function

# Create your views here.
def about(request):
    template_name = "organisation/about.html"
    context={}
        
    context.update({
            'menu': "about",
            'functions': Function.objects.active(),
        })
    return render(request, template_name, context)