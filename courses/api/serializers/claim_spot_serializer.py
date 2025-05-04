from rest_framework.serializers import ModelSerializer

from ...models import Attendance


class ClaimSpotSerializer(ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["lesson_occurrence", "role"]
