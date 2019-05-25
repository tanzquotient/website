from django.db import models


class RegularLessonCancellation(models.Model):
    course = models.ForeignKey('Course', related_name='cancellations', on_delete=models.CASCADE)
    date = models.DateField(blank=False, null=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return "{}".format(self.date.strftime('%d.%m.%Y'))
