from collections import defaultdict

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from courses.models import Teach


def get_teachers_overview_data() -> list[list]:
    grouped_teachings = defaultdict(lambda: defaultdict(list))
    for teaching in Teach.objects.order_by('teacher__first_name', 'teacher__last_name').prefetch_related(
            'teacher', 'course__irregular_lessons', 'course__regular_lessons', 'course__offering__period',
            'course__period').all():

        if teaching.course.is_external() or teaching.course.cancelled:
            continue

        first_lesson_date = teaching.course.get_first_lesson_date()
        year = str(first_lesson_date.year) if first_lesson_date else _('unknown year')
        grouped_teachings[teaching.teacher_id][year].append(teaching)

    rows = []

    years = sorted({year for group in grouped_teachings.values() for year in group.keys()})

    header = [_('First name'), _('Last name')] + years + [_('Total years'), _('Total courses')]
    rows.append(header)

    for grouped_by_year in grouped_teachings.values():
        teacher: User = list(grouped_by_year.values())[0][0].teacher
        row = [teacher.first_name, teacher.last_name]

        for year in years:
            if year not in grouped_by_year:
                row.append('-')
            else:
                row.append(len(grouped_by_year[year]))

        # Number of years the teacher has been teaching (counting unknown year as one year)
        row.append(len(grouped_by_year.values()))

        row.append(sum([len(t) for t in grouped_by_year.values()]))

        rows.append(row)

    return rows
