from django.contrib import auth
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    student_status = serializers.StringRelatedField(source="profile.student_status")

    class Meta:
        model = auth.get_user_model()
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "student_status",
        )
