from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_GET

from .models import Destination, Source, Visit


@require_GET
def redirect_to_destination(request):
    try:
        source_ids = request.GET.getlist("f")
        destination_ids = request.GET.getlist("t")
        if len(source_ids) != 1 or len(destination_ids) != 1:
            raise ValueError

        source = Source.objects.get(pk=source_ids[0])
        destination = Destination.objects.get(pk=destination_ids[0])
    except (Destination.DoesNotExist, KeyError, Source.DoesNotExist, ValueError):
        return HttpResponse(
            "Ooops, something went wrong...", content_type="text/plain", status=404
        )

    Visit.objects.create(source=source, destination=destination)
    return HttpResponseRedirect(
        destination_url_with_forwarded_parameters(destination.url, request)
    )


def destination_url_with_forwarded_parameters(destination_url, request):
    forwarded_parameters = [
        (name.removeprefix("q_"), value)
        for name, values in request.GET.lists()
        if name.startswith("q_")
        for value in values
    ]
    if not forwarded_parameters:
        return destination_url

    destination_parts = urlsplit(destination_url)
    forwarded_names = {name for name, _ in forwarded_parameters}
    destination_parameters = [
        (name, value)
        for name, value in parse_qsl(destination_parts.query, keep_blank_values=True)
        if name not in forwarded_names
    ]
    return urlunsplit(
        destination_parts._replace(
            query=urlencode(destination_parameters + forwarded_parameters)
        )
    )
