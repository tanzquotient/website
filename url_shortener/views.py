from urllib.parse import urlsplit, urlunsplit

from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import ShortLink, Visit


@require_GET
def redirect_to_destination(request, tag):
    try:
        now = timezone.now()
        short_link = (
            ShortLink.objects.select_related("destination")
            .only("id", "destination_id", "destination__url")
            .filter(deactivated=False, tag=tag)
            .filter(Q(valid_from__isnull=True) | Q(valid_from__lte=now))
            .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=now))
            .get()
        )
    except ShortLink.DoesNotExist:
        return HttpResponse(
            "Ooops, something went wrong...", content_type="text/plain", status=404
        )

    Visit.objects.create(
        short_link_id=short_link.id,
        user_id=request.user.id if request.user.is_authenticated else None,
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
    return urlunsplit(destination_parts._replace(query=query))
