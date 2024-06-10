from rest_framework import serializers

from courses.models import Style


class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
