import json
from typing import Iterable

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpRequest, HttpResponse

from groups.definitions import GroupDefinitions


@login_required
def search_teacher(request: HttpRequest):
    if not request.user.is_staff and not request.user.profile.is_teacher():
        raise PermissionDenied

    search_string: str = request.GET.get("q", "").strip()
    limit: int = int(request.GET.get("limit", "10").strip())

    teacher_query = Q(groups__name=GroupDefinitions.ALL_TEACHERS.name)
    current_teacher_query = Q(groups__name=GroupDefinitions.CURRENT_TEACHERS.name)

    if not search_string:
        return return_search_results(User.objects.filter(current_teacher_query).all())

    terms = set(search_string.split())

    email_exact_match = Q(email__in=terms)
    name_exact_match = Q(first_name__in=terms) & Q(last_name__in=terms)
    exact_query = email_exact_match | name_exact_match

    starts_with_query = Q()
    for term in terms:
        starts_with_query &= Q(first_name__istartswith=term) | Q(
            last_name__istartswith=term
        )

    # Exact matches and current teachers
    users = merge_users(
        get_users(exact_query),
        get_users(starts_with_query & current_teacher_query),
        limit,
    )

    # Fill up with non-current teachers
    if len(users) < limit:
        users = merge_users(users, get_users(starts_with_query & teacher_query), limit)

    # Fill up with anyone if allowed
    if len(users) < limit and request.user.is_staff:
        users = merge_users(users, get_users(starts_with_query), limit)

    return return_search_results(users)


def get_users(query: Q) -> Iterable[User]:
    return User.objects.filter(query).order_by("first_name", "last_name")


def merge_users(
    first: Iterable[User], second: Iterable[User], limit: int
) -> list[User]:
    merged = list(first)[:limit]
    if len(merged) < limit:
        for user in second:
            if user not in merged:
                merged.append(user)
            if len(merged) >= limit:
                break
    return merged


def return_search_results(users: Iterable[User]) -> HttpResponse:
    search_results = [
        {
            "value": user.id,
            "text": f"{user.first_name} {user.last_name}",
        }
        for user in users
    ]
    return HttpResponse(json.dumps(search_results), content_type="application/json")
