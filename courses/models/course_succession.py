from django.db import models


class CourseSuccession(models.Model):
    predecessor = models.ForeignKey('Course', related_name="successing_courses_through", on_delete=models.CASCADE)
    successor = models.ForeignKey('Course', related_name="preceding_courses_through", on_delete=models.CASCADE)

    def __str__(self):
        return "{} precedes {}".format(self.predecessor, self.successor)
