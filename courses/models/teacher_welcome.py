from django.db import models
from post_office.models import Email


class TeacherWelcome(models.Model):
    teach = models.ForeignKey('Teach', related_name='teacher_welcomes', on_delete=models.CASCADE)
    date = models.DateField(blank=False, null=False, auto_now_add=True)
    date.help_text = "The date when the welcome mail was sent to the teacher."
    mail = models.ForeignKey(Email, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "({}) welcomed at {}".format(self.teach, self.date)
