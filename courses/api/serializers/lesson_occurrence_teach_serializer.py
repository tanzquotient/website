from rest_framework.fields import IntegerField
from rest_framework.serializers import ModelSerializer

from courses.models import LessonOccurrenceTeach
from . import UserSerializer


class LessonOccurrenceTeachSerializer(ModelSerializer):
    teacher = UserSerializer(read_only=True)
    teacher_id = IntegerField(write_only=True)

    class Meta:
        model = LessonOccurrenceTeach
        exclude = ["hourly_wage"]
