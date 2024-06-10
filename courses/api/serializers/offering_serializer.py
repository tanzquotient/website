from rest_framework import serializers

from courses.models import Offering


class OfferingSerializer(serializers.HyperlinkedModelSerializer):
    course_set = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="courses:api:course-payment-detail"
    )
    period = serializers.StringRelatedField()

    class Meta:
        model = Offering
        fields = ("id", "name", "period", "course_set")
