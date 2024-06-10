from rest_framework import serializers

from courses.models import CourseType


class CourseTypeSerializer(serializers.HyperlinkedModelSerializer):
    styles = serializers.HyperlinkedRelatedField(
        many=True, view_name="courses:api:style-detail", read_only=True
    )

    class Meta:
        model = CourseType
        fields = ("name", "styles", "level", "couple_course")
