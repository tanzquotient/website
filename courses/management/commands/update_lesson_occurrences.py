import logging

from django.core.management.base import BaseCommand

from courses.models import Course

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Updates lesson occurrences"

    def handle(self, *args, **options) -> None:
        num_courses = Course.objects.count()
        courses: list[Course] = (
            Course.objects.prefetch_related(
                "regular_lessons__exceptions__lesson_details__room",
                "irregular_lessons__lesson_details__room",
                "irregular_lessons__course__room",
                "regular_lessons__course__room",
                "period__cancellations",
                "offering__period__cancellations",
            )
            .order_by("period__date_from", "offering__period__date_from")
            .all()
        )

        for count, course in enumerate(courses, 1):
            course.update_lesson_occurrences()
            logger.info(f"Completed {count} out of {num_courses}.")
