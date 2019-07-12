from django.core.exceptions import FieldDoesNotExist
from django.db import models


class LessonDetails(models.Model):
    room = models.ForeignKey('Room', related_name='lessons', blank=True, null=True, on_delete=models.PROTECT)

    def get_course(self):
        return self.get_lesson().course

    def get_lesson(self):
        from courses.models import IrregularLesson
        try:
            return self.irregular_lesson
        except IrregularLesson.DoesNotExist:
            return self.regular_lesson_exception.regular_lesson

    def __str__(self):
        strings = []
        if self.room:
            strings.append(str(self.room))
        strings += [t.teacher.get_full_name() for t in self.teaching.all()]

        return ", ".join(strings)
