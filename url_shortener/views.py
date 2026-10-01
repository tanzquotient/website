from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_GET

from .models import Destination, Source, Visit


@require_GET
def redirect_to_destination(request):
    try:
        source = Source.objects.get(pk=request.GET["f"])
        destination = Destination.objects.get(pk=request.GET["t"])
    except (Destination.DoesNotExist, KeyError, Source.DoesNotExist, ValueError):
        return HttpResponse(
            "Ooops, something went wrong...", content_type="text/plain", status=404
        )

    Visit.objects.create(source=source, destination=destination)
    return HttpResponseRedirect(destination.url)
