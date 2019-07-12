from django.conf import settings
from django.db import models


class Teach(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='teaching_courses', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', related_name='teaching', on_delete=models.CASCADE)
    welcomed = models.BooleanField(default=False)
    hourly_wage = models.FloatField(blank=True, null=True)
    hourly_wage.help_text = 'Hourly wage, leave empty to copy default wage from teacher profile.'

    def get_wage(self):
        time = self.course.get_total_time()['total']
        if time is None or self.hourly_wage is None:
            return None

        return time * self.hourly_wage

    def save(self, *args, **kwargs):
        if self.hourly_wage is None:
            self.hourly_wage = self.teacher.profile.default_hourly_wage
        super(Teach, self).save(*args, **kwargs)

    def __str__(self):
        return '{} teaches {}'.format(self.teacher, self.course)

