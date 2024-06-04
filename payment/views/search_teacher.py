import json

from django.http import HttpRequest, HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from courses.models import Course


@login_required
def search_teacher(request: HttpRequest, course: int):

    if not request.user.is_staff and not request.user.profile.is_teacher():
        raise PermissionDenied

    search_string: str = request.GET.get("q", None)
    course: Course = Course.objects.get(id=course)
    course_teachers = course.get_teachers()
    users = []

    if len(search_string) == 0:
        users = sorted([
            {
                "value": course_teacher.id,
                "text": f"{course_teacher.first_name} {course_teacher.last_name}",
            }
            for course_teacher in course_teachers
        ], key=lambda u: u["text"])

    elif len(search_string) > 3:
        query_exact = Q()
        query_contains = Q()

        if " " in search_string:
            # search_string cannot be an email address, split it by whitespace
            split_search_string = search_string.split(" ")
            for i in range(1, len(split_search_string)):
                split_1 = " ".join(split_search_string[:i])
                split_2 = " ".join(split_search_string[i:])
                # look for exact (first name, last name) match
                query_exact.add(
                    Q(first_name__iexact=split_1, last_name__iexact=split_2)
                    | Q(first_name__iexact=split_2, last_name__iexact=split_1),
                    Q.OR,
                )
                # look for partial (first name, last name) match
                query_contains.add(
                    Q(first_name__istartswith=split_1, last_name__istartswith=split_2)
                    | Q(first_name__istartswith=split_2, last_name__istartswith=split_1),
                    Q.OR,
                )
        else:
            # look for exact email match
            query_exact.add(Q(email__iexact=search_string), Q.OR)
            # look for partial first name, last name or email match
            query_contains.add(
                Q(first_name__istartswith=search_string)
                | Q(last_name__istartswith=search_string)
                | Q(email__icontains=search_string),
                Q.OR,
            )

        users_exact = sorted(
            list(User.objects.filter(query_exact).all()), key=lambda user: user.id
        )
        users_contains = sorted(
            list(User.objects.filter(query_contains).all()), key=lambda user: user.id
        )
        # remove non-exact non-teacher matches if query sender is not staff
        if not request.user.is_staff:
            users_contains = list(
                filter(lambda user: user.profile.is_teacher(), users_contains)
            )
        users_list = users_exact + users_contains
        # remove duplicates
        users_list = list(dict.fromkeys(users_list))
        users = [
            {
                "value": user.id,
                "text": f"{user.first_name} {user.last_name}",
            }
            for user in users_list
        ]

    return HttpResponse(json.dumps(users), content_type="application/json")
