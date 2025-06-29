from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from ..serializers import ClaimSpotSerializer
from ...models import (
    Attendance,
    LessonOccurrence,
    LeadFollow,
    AttendanceState,
    SubscribeState,
    Subscribe,
)
from ...utils import lesson_lead_follow_balance


class ClaimSpotApiView(APIView):

    @transaction.atomic
    def post(self, request: Request) -> Response:
        serializer = ClaimSpotSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

        user = request.user
        data = serializer.data
        lesson_occurrence = get_object_or_404(
            LessonOccurrence, pk=data["lesson_occurrence"]
        )

        # A spot can only be claimed as either a leader of follower
        role = data["role"]
        lead_follow = [LeadFollow.LEAD, LeadFollow.FOLLOW]
        if role not in lead_follow:
            raise ValidationError(detail=f"Role not set. Must be one of {lead_follow}")

        # Only one attendance object is allowed per user and lesson
        if Attendance.objects.filter(
            user=user,
            lesson_occurrence=lesson_occurrence,
        ).exists():
            raise ValidationError(detail="Attendance already set for this lesson.")

        # User must not be a participant of this course
        course = lesson_occurrence.course
        if Subscribe.objects.filter(
            user=user,
            course=course,
            state__in=SubscribeState.ACCEPTED_STATES,
        ).exists():
            raise ValidationError(detail="You are a participant of this course.")

        # Check if the user is allowed to claim the spot
        if course.type not in user.skill.unlocked_course_types.all():
            raise ValidationError(detail="Requirements not met.")

        # Check if the balance improves if a spot is claimed with this role
        balance_diff = 1 if role == LeadFollow.LEAD else -1
        lesson_balance = lesson_lead_follow_balance(lesson_occurrence)
        if abs(lesson_balance + balance_diff) >= abs(lesson_balance):
            raise ValidationError("No spots for selected role available.")

        # Create the attendance object to claim spot
        Attendance.objects.create(
            user=user,
            lesson_occurrence=lesson_occurrence,
            role=role,
            state=AttendanceState.REPLACEMENT,
        )

        return Response(data=data)
