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
    AttendanceState,
)
from ...utils import change_attendance_window_open


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

        if not change_attendance_window_open(lesson_occurrence):
            raise ValidationError(detail="You can not change your attendance anymore.")

        # Special case: replacement cancels
        if state == AttendanceState.ABSENT_EXCUSED and (
            Attendance.objects.filter(
                lesson_occurrence=lesson_occurrence,
                user=user,
                state=AttendanceState.REPLACEMENT,
            ).exists()
        ):
            Attendance.objects.filter(
                lesson_occurrence=lesson_occurrence,
                user=user,
            ).delete()
            data["is_replacement"] = True
            return Response(data=data)

        # Regular case: participant attendance
        subscription = get_object_or_404(
            Subscribe,
            user=user,
            course=lesson_occurrence.course,
            state__in=SubscribeState.ACCEPTED_STATES,
        )
        if subscription.lead_follow == LeadFollow.NO_PREFERENCE:
            raise ValidationError(
                detail="Make sure you have a role set for this course."
            )

        if state == Attendance.DEFAULT_STATE:
            Attendance.objects.filter(
                lesson_occurrence=lesson_occurrence, user=user
            ).delete()
        else:
            attendance, _ = Attendance.objects.get_or_create(
                user=user,
                lesson_occurrence=lesson_occurrence,
                role=subscription.lead_follow,
            )
            attendance.state = state
            attendance.save()

        return Response(data=data)
