from urllib.parse import urlsplit, urlunsplit

from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_GET

from .models import ShortLink, Visit


@require_GET
def redirect_to_destination(request, tag):
    try:
        short_link = ShortLink.objects.select_related("source", "destination").get(
            active=True, tag=tag
        )
    except ShortLink.DoesNotExist:
        return HttpResponse(
            "Ooops, something went wrong...", content_type="text/plain", status=404
        )

    Visit.objects.create(
        short_link=short_link,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.headers.get("User-Agent", ""),
    )
    return HttpResponseRedirect(
        destination_url_with_request_parameters(short_link.destination.url, request)
    )


def destination_url_with_request_parameters(destination_url, request):
    query_string = request.META.get("QUERY_STRING", "")
    if not query_string:
        return destination_url

    destination_parts = urlsplit(destination_url)
    query = "&".join(filter(None, (destination_parts.query, query_string)))
    return urlunsplit(
        destination_parts._replace(query=query)
    )
