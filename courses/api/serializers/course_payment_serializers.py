from rest_framework import serializers

from courses.api.serializers.subscribe_payment_serializer import (
    SubscribePaymentSerializer,
)
from courses.models import Course


class CoursePaymentSerializer(serializers.HyperlinkedModelSerializer):
    offering = serializers.HyperlinkedRelatedField(
        view_name="courses:api:offering-detail", read_only=True
    )
    type_name = serializers.StringRelatedField(source="type")
    type = serializers.HyperlinkedRelatedField(
        view_name="courses:api:coursetype-detail", read_only=True
    )
    # this calls the method participatory() and serializes the returned queryset
    participatory = SubscribePaymentSerializer(many=True)

    class Meta:
        model = Course
        fields = ("id", "name", "type_name", "type", "offering", "participatory")
