from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from ...models import (
    Attendance,
    AttendanceState,
    LeadFollow,
    LessonOccurrence,
    Subscribe,
    SubscribeState,
)
from ...utils import change_attendance_window_open
from ..serializers import MyAttendanceSerializer


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

        subscription = Subscribe.objects.filter(
            user=user,
            course=lesson_occurrence.course,
            state__in=SubscribeState.ACCEPTED_STATES,
        ).first()

        # Special case: replacement cancels (a spot claimed before joining the course
        # is ignored, the user is handled as a regular participant then)
        if (
            subscription is None
            and state == AttendanceState.ABSENT_EXCUSED
            and Attendance.objects.filter(
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
        if subscription is None:
            raise Http404

        role = subscription.assigned_role()
        if role == LeadFollow.NO_PREFERENCE:
            raise ValidationError(
                detail="Make sure you have a role set for this course."
            )

        if state == Attendance.DEFAULT_STATE:
            Attendance.objects.filter(
                lesson_occurrence=lesson_occurrence, user=user
            ).delete()
        else:
            Attendance.objects.update_or_create(
                user=user,
                lesson_occurrence=lesson_occurrence,
                defaults={"role": role, "state": state},
            )

        return Response(data=data)
