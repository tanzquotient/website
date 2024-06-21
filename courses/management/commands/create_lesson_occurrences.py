import logging

from django.core.management.base import BaseCommand

from courses.models import Course, LessonOccurrenceTeach

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates/updates lesson occurrences for existing courses"

    def add_arguments(self, parser):
        parser.add_argument(
            "--update_teachers",
            action="store_true",
            help="Also updates the teachers of each lesson occurrences "
            "based on the course teachers.",
        )

        parser.add_argument(
            "--over_only", action="store_true", help="Only affect courses that are over"
        )

    def handle(self, *args, **options):
        num_courses = Course.objects.count()
        courses: list[Course] = Course.objects.all().order_by(
            "period__date_from", "offering__period__date_from"
        )

        for count, course in enumerate(courses, 1):
            if not (options["over_only"] and course.is_over()):
                logger.debug(f"Skipping course {course.name} since it is not over.")
                continue

            logger.debug(f"Creating lesson occurrences for course {course.name}")
            course.update_lesson_occurrences()
            lesson_occurrences = course.lesson_occurrences.all()
            logger.debug(f"Updated lesson occurrences: {lesson_occurrences}")

            if options["update_teachers"]:
                teachers = course.get_teachers()
                logger.debug(f"Updating teachers from course {course.name}")
                for lesson_occurrence in lesson_occurrences:
                    for teacher in teachers:
                        LessonOccurrenceTeach.objects.get_or_create(
                            lesson_occurrence=lesson_occurrence,
                            teacher=teacher,
                        )

            logger.info(f"Completed {count} out of {num_courses}.")
