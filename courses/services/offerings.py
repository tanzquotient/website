from datetime import date

from django.db.models import Q, Prefetch, QuerySet
from django.http import Http404, HttpRequest
from django.utils import dateformat
from django.utils.translation import gettext as _

from courses import models as models
from courses.managers import CourseManager
from courses.models import Offering, OfferingType, IrregularLesson, RegularLessonException, Weekday, Course
from courses.services.general import log


def get_all_offerings():
    return Offering.objects.order_by('period__date_from', '-active')


def get_offerings_to_display(preview: bool = False) -> QuerySet[Offering]:
    """return offerings that have display flag on and order them by start date in ascending order"""

    queryset = Offering.objects.exclude(type=OfferingType.PARTNER)

    if preview:
        queryset = queryset.filter(Q(display=True) | Q(preview=True))
    else:
        queryset = queryset.filter(display=True)

    return queryset.select_related('period').prefetch_related('period__cancellations').order_by('-period__date_from')


def get_historic_offerings(offering_type=None):

    queryset = Offering.objects.all()
    if offering_type:
        queryset = Offering.objects.filter(type=offering_type)

    offerings = [o for o in queryset if o.is_historic() and o.has_date_from()]
    offerings_dict = {}

    for offering in offerings:
        year = offering.get_start_year()
        if year not in offerings_dict:
            offerings_dict[year] = []
        offerings_dict[year].append(offering)

    return sorted([(k, v) for k, v in offerings_dict.items()], key=lambda t: t[0], reverse=True)


def get_sections(offering, course_filter=None):
    offering_sections = []
    course_set = offering.course_set.select_related('period', 'type', 'room').prefetch_related(
        'regular_lessons',
        Prefetch('irregular_lessons', queryset=IrregularLesson.objects.order_by('date', 'time_from')),
        Prefetch('regular_lessons__exceptions', queryset=RegularLessonException.objects.order_by('date')),
        'period__cancellations',
    )

    if not course_filter:
        course_filter = lambda c: True

    if offering.type == OfferingType.REGULAR:
        for (w, w_name) in Weekday.CHOICES:
            courses_on_weekday = [c for c in CourseManager.weekday(course_set, w) if course_filter(c)]
            if courses_on_weekday:
                offering_sections.append({
                    'section_title': Weekday.WEEKDAYS_TRANSLATIONS_DE[w],
                    'courses': courses_on_weekday
                })

        courses_without_weekday = [c for c in CourseManager.weekday(course_set, None) if course_filter(c)]
        if courses_without_weekday:
            offering_sections.append({'section_title': _("Irregular weekday"), 'courses': courses_without_weekday})

    elif offering.type in [OfferingType.IRREGULAR, OfferingType.PARTNER]:
        courses_by_month = CourseManager.by_month(course_set)
        for (d, courses) in courses_by_month:
            if d is None:
                section_title = _("Unknown month")
            elif 1 < d.month <= 12:
                # use the django formatter for date objects
                section_title = dateformat.format(d, 'F Y')
            else:
                section_title = ""
            # filter out undisplayed courses if not staff user
            courses = [c for c in courses if course_filter(c)]
            # tracks if at least one period of a course is set (it should be displayed on page)
            deviating_period = False
            for c in courses:
                if c.period:
                    deviating_period = True
                    break

            if courses:
                offering_sections.append(
                    {'section_title': section_title, 'courses': courses, 'hide_period_column': not deviating_period})
    else:
        message = "unsupported offering type"
        log.error(message)
        raise Http404(message)

    return offering_sections


def get_upcoming_courses_without_offering():
    courses = Course.objects.filter(
        display=True, offering__isnull=True
    )

    return [course for course in courses if not course.is_over()]


def get_current_active_offering():
    return models.Offering.objects.filter(active=True).order_by('period__date_from').first()


def get_subsequent_offering():
    res = models.Offering.objects.filter(period__date_from__gte=date.today()).order_by(
        'period__date_from').all()
    if len(res) > 0:
        return res[0]
    else:
        return None
