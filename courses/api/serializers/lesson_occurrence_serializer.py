from rest_framework.serializers import ModelSerializer

from . import UserSerializer
from courses.models import LessonOccurrence


class LessonOccurrenceSerializer(ModelSerializer):
    teachers = UserSerializer(many=True, read_only=True)

    class Meta:
        model = LessonOccurrence
        fields = "__all__"
