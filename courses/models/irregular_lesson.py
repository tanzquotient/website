import datetime

from django.db import models

from . import Room


class IrregularLesson(models.Model):
    course = models.ForeignKey('Course', related_name='irregular_lessons', on_delete=models.CASCADE)
    date = models.DateField(blank=False, null=False)
    time_from = models.TimeField()
    time_to = models.TimeField()
    room = models.ForeignKey(Room, related_name='irregular_lessons', blank=True, null=True, on_delete=models.PROTECT)
    room.help_text = "The room for this lesson. If left empty, the course room is assumed."

    class Meta:
        ordering = ['date', 'time_from']

    def get_total_time(self):
        return datetime.datetime.combine(self.date, self.time_to) - datetime.datetime.combine(self.date, self.time_from)

    def __str__(self):
        s = "{}, {}-{}".format(self.date, self.time_from.strftime("%H:%M"),
                               self.time_to.strftime("%H:%M"))
        if self.room:
            s = s + ", {}".format(self.room)
        return s