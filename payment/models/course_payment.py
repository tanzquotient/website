from django.db import models

from courses.models import Course
from . import Payment


class CoursePayment(models.Model):
    """
    A Course Payment is a matched intermediate object.
    """
    payment = models.ForeignKey(Payment, related_name='course_payments', on_delete=models.PROTECT)
    course = models.ForeignKey(Course, related_name='course_payments', on_delete=models.PROTECT)
    amount = models.FloatField()