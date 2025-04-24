from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from ..serializers import MyAttendanceSerializer
from ...models import (
    Attendance,
    LessonOccurrence,
    Subscribe,
    LeadFollow,
    SubscribeState,
)


class MyAttendanceApiView(APIView):

    def post(self, request: Request) -> Response:
        serializer = MyAttendanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

        user = request.user
        data = serializer.data
        state = data["state"]
        lesson_occurrence = get_object_or_404(
            LessonOccurrence, pk=data["lesson_occurrence"]
        )

        if Subscribe.objects.filter(
            user=user,
            course=lesson_occurrence.course,
            state__in=SubscribeState.ACCEPTED_STATES,
            lead_follow=LeadFollow.NO_PREFERENCE,
        ).exists():
            raise ValidationError(
                detail="Make sure you have a role set for this course."
            )

        if state == Attendance.DEFAULT_STATE:
            Attendance.objects.filter(
                lesson_occurrence=lesson_occurrence, user=user
            ).delete()
        else:
            attendance, _ = Attendance.objects.get_or_create(
                user=user, lesson_occurrence=lesson_occurrence
            )
            attendance.state = state
            attendance.save()

        return Response(data=data)
