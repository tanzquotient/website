from django.db import models

from . import managers

# Create your models here.
class QuestionGroup(models.Model):
    name = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return u"{}".format(self.name)


class Question(models.Model):
    question_text = models.TextField()
    answer_text = models.TextField()
    display = models.BooleanField(default=True)
    question_group = models.ForeignKey('QuestionGroup', related_name='questions')

    # position field for ordering columns (grappelli feature)
    position = models.PositiveSmallIntegerField("Position", default=0)

    class Meta:
        ordering = ['position']

    objects = managers.QuestionManager()

    def __str__(self):
        return u"{}".format(self.question_text)
