from collections import defaultdict

import reversion
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404
from reversion.models import Version

from ..models import Answer


def show_or_hide_answer_on_post(request: HttpRequest) -> None:
    answer_id = request.POST.get('answer', None)
    if answer_id:
        hide = 'hide_answer' in request.POST
        comment = request.POST.get('comment', None)
        answer = get_object_or_404(Answer, id=answer_id)
        if answer.hide_from_public_reviews != hide:
            with reversion.create_revision():
                answer.hide_from_public_reviews = hide
                answer.save()

                reversion.set_user(request.user)
                fallback_comment = "Answer was hidden." if hide else "Answer was made visible again."
                reversion.set_comment(comment or fallback_comment)


@staff_member_required
def changed_answers(request: HttpRequest) -> HttpResponse:
    show_or_hide_answer_on_post(request)

    grouped_by_version = defaultdict(list)
    for version in Version.objects.get_for_model(Answer).all():
        grouped_by_version[version.object].append((version.revision, version.field_dict))

    changed_answers = sorted([(key, values) for key, values in grouped_by_version.items() if len(values) > 1],
                             key=lambda t: t[0].survey_instance.last_update, reverse=True)

    return render(request, "survey/changed_answers.html", context=dict(changed_answers=changed_answers))
