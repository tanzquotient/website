from collections import defaultdict

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from reversion.models import Version

from ..models import Answer


@staff_member_required
def hidden_answers(request: HttpRequest) -> HttpResponse:
    hidden_answers = list(Answer.objects.filter(hide_from_public_reviews=True).all())
    hidden_answers_object_ids = {str(answer.id) for answer in hidden_answers}
    versions = list(Version.objects.get_for_model(Answer)
                    .exclude(revision__comment='Initial version.')
                    .filter(object_id__in=hidden_answers_object_ids).order_by('-revision__date_created')
                    .all())

    grouped_by_version = defaultdict(list)
    for version in versions:
        grouped_by_version[version.object].append(version.revision)

    return render(request, "survey/hidden_answers.html", context=dict(grouped_by_version=grouped_by_version.items()))
