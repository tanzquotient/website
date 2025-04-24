from rest_framework.serializers import ModelSerializer

from ...models import Attendance


class MyAttendanceSerializer(ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["lesson_occurrence", "state"]
