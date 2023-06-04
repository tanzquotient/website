from django.shortcuts import render

from email_system import services


# Create your views here.
def unsubscribe(request, context, user_id, code):
    success = services.unsubscribe(context, user_id, code)
    context = dict(success=success)
    return render(request, "email_system/unsubscribe.html", context)
