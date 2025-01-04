from django.utils.translation import gettext_lazy as _
from courses.models import LessonOccurrence
from decimal import Decimal


def get_teachers_overview_data() -> list[list]:
    lesson_occurrences = (
        LessonOccurrence.objects.prefetch_related("teachers", "course")
        .exclude(course__cancelled=True)
        .order_by("start")
        .all()
    )
    years = range(
        lesson_occurrences.first().start.year,
        lesson_occurrences.last().start.year + 1,
    )
    header = (
        [_("First name"), _("Last name")]
        + list(years)
        + [_("Total years"), _("Total hours")]
    )
    teachers_data = dict()
    for l in lesson_occurrences:
        if l.course.is_external():
            continue
        for t in l.teachers.all():
            teachers_data.setdefault(
                t,
                {y: Decimal(0) for y in years},
            )
            teachers_data[t][l.start.year] += l.get_hours()

    rows = []
    for t, t_data in teachers_data.items():
        rows.append(
            [t.first_name, t.last_name]
            + [round(t_data[y], 2) or "-" for y in years]
            + [
                len(years) - list(t_data.values()).count(Decimal(0)),
                round(sum(t_data.values(), Decimal(0)), 2),
            ]
        )

    sorted_rows = sorted(rows, key=lambda r: (r[-1]), reverse=True)
    return [header] + sorted_rows
