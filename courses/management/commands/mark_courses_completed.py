import logging

from django.core.management.base import BaseCommand

from courses.models import Course, LessonOccurrenceTeach

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates/updates lesson occurrences for existing courses"

    def add_arguments(self, parser):
        parser.add_argument(
            "--n_days",
            action="store",
            help="Min. days since end of course for it to be marked as completed",
        )

    def handle(self, *args, **options):

        courses: list[Course] = Course.objects.all().order_by(
            "period__date_from", "offering__period__date_from"
        )
        num_courses = courses.count()

        for count, course in enumerate(courses, 1):
            if (options["n_days"] is None and course.is_over()) or course.is_over_since(
                days=options["n_days"]
            ):
                course.completed = True
                course.save()
                logger.debug(
                    f"Course {count}/{num_courses} ({course}) marked as completed"
                )
            else:
                logger.debug(f"Course {count}/{num_courses} ({course}) skipped")
