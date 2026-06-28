from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from email_system import services


@csrf_exempt
def unsubscribe(request, context, user_id, code):
    if request.method == "POST":
        if request.POST.get("List-Unsubscribe") == "One-Click":
            # RFC 8058 one-click from an email client
            success = services.unsubscribe(context, user_id, code)
            return render(
                request,
                "email_system/unsubscribe.html",
                {"done": True, "success": success},
            )
        if request.POST.get("confirm") == "1":
            # Manual button click from the confirmation form
            success = services.unsubscribe(context, user_id, code)
            return render(
                request,
                "email_system/unsubscribe.html",
                {"done": True, "success": success},
            )
        # POST without a recognised marker (e.g. automated scanner) → show button
    return render(
        request,
        "email_system/unsubscribe.html",
        {
            "done": False,
            "context": context,
            "user_id": user_id,
            "code": code,
        },
    )
