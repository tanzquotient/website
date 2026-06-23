from rest_framework.serializers import ModelSerializer

from courses.models import LessonOccurrence

from . import UserSerializer


class LessonOccurrenceSerializer(ModelSerializer):
    teachers = UserSerializer(many=True, read_only=True)

    class Meta:
        model = LessonOccurrence
        fields = "__all__"
