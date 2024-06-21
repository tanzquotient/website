from django.core.management.base import BaseCommand, CommandError
from courses.models import Course, LessonOccurrenceTeach


class Command(BaseCommand):
    help = "Creates/updates lesson occurrences for existing courses"

    def add_arguments(self, parser):
        parser.add_argument(
            "--empty_teachers",
            action="store_true",
            help="Remove teachers from lesson occurrences",
        )

        parser.add_argument(
            "--populate",
            action="store_true",
            help="Populate created lesson occurrences with main teachers (typically in combination with --empty-teachers)",
        )

        parser.add_argument(
            "--over_only", action="store_true", help="Only affect courses that are over"
        )

    def handle(self, *args, **options):
        courses: list[Course] = Course.objects.all().order_by("period__date_from")

        for course in courses:
            if options["over_only"] and course.is_over():
                continue

            course.update_lesson_occurrences()

            for lesson_occurrence in course.lesson_occurrences.all():
                if options["empty_teachers"]:
                    LessonOccurrenceTeach.objects.filter(
                        lesson_occurrence=lesson_occurrence
                    ).delete()

                if options["populate"]:
                    for teacher in course.get_teachers():
                        LessonOccurrenceTeach.objects.create(
                            lesson_occurrence=lesson_occurrence,
                            teacher=teacher,
                        )
