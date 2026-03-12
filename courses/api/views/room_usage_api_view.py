from datetime import datetime, time, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from ...models import LessonOccurrence, Room
from events.models import Event
from django.db.models import Q


class RoomUsageApiView(APIView):
    """Return lesson occurrences for a room within a given datetime range.

    GET params:
    - room_id: int (required)
    - fromDate / from: ISO datetime or YYYY-MM-DD (required)
    - toDate / to: ISO datetime or YYYY-MM-DD (required)
    """

    permission_classes = [IsAdminUser]

    def get(self, request: Request) -> Response:
        room_id = request.query_params.get("room_id")
        if not room_id:
            return Response({"detail": "room_id is required"}, status=HTTP_400_BAD_REQUEST)

        room = get_object_or_404(Room, pk=room_id)

        from_str = (
            request.query_params.get("fromDate")
            or request.query_params.get("from")
            or request.query_params.get("from_datetime")
        )
        to_str = (
            request.query_params.get("toDate")
            or request.query_params.get("to")
            or request.query_params.get("to_datetime")
        )

        if not from_str or not to_str:
            return Response({"detail": "fromDate and toDate are required"}, status=HTTP_400_BAD_REQUEST)

        def _parse(s: str, is_end: bool = False):
            # try full datetime first
            dt = parse_datetime(s)
            if dt:
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
                return dt
            # try date only
            d = parse_date(s)
            if d:
                if is_end:
                    return timezone.make_aware(datetime.combine(d, time.max), timezone.get_current_timezone())
                return timezone.make_aware(datetime.combine(d, time.min), timezone.get_current_timezone())
            return None

        start_dt = _parse(from_str, is_end=False)
        end_dt = _parse(to_str, is_end=True)

        if not start_dt or not end_dt:
            return Response({"detail": "Could not parse fromDate/toDate"}, status=HTTP_400_BAD_REQUEST)

        # include events from the Event model (explicit events assigned to rooms)
        # and occurrences where the lesson.room is None but the course's room matches (course)
        # Event objects use date/time fields; compute their datetimes in Python and
        # include those that overlap the requested interval.

        results = []

        # Events
        start_date = start_dt.date()
        end_date = end_dt.date()

        events_qs = (
            Event.objects.filter(room=room)
            .filter(date__lte=end_date)
            .filter(Q(date_to__gte=start_date) | Q(date_to__isnull=True, date__gte=start_date))
            .order_by("date")
            .all()
        )

        for ev in events_qs:
            # compute event start/end datetimes similar to events.ical.EventFeed
            event_start = (
                timezone.make_aware(datetime.combine(ev.date, ev.time_from or time.min), timezone.get_current_timezone())
                if ev.time_from is not None
                else timezone.make_aware(datetime.combine(ev.date, time.min), timezone.get_current_timezone())
            )

            date_to = ev.date_to or ev.date
            event_end = (
                timezone.make_aware(datetime.combine(date_to, ev.time_to), timezone.get_current_timezone())
                if ev.time_to is not None
                else timezone.make_aware(datetime.combine(date_to + timedelta(days=1), time.min), timezone.get_current_timezone())
            )

            # include only if overlaps requested interval
            if event_end >= start_dt and event_start <= end_dt:
                results.append(
                    {
                        "id": ev.id,
                        "title": ev.get_name() if hasattr(ev, "get_name") else str(ev),
                        "start": timezone.localtime(event_start).strftime("%Y-%m-%d %H:%M:%S"),
                        "end": timezone.localtime(event_end).strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "event",
                        "location": ev.room.name if ev.room else None,
                    }
                )

        # Lesson occurrences (courses)
        occurrences = (
            LessonOccurrence.objects.select_related("course", "room", "course__type")
            .filter(
                Q(room=room) | Q(room__isnull=True) & Q(course__room=room),
                start__gte=start_dt,
                end__lte=end_dt,
            )
            .order_by("start")
            .all()
        )

        for occ in occurrences:
            results.append(
                {
                    "id": occ.id,
                    "title": occ.course.type.title if hasattr(occ.course, "type") else str(occ.course),
                    "start": timezone.localtime(occ.start).strftime("%Y-%m-%d %H:%M:%S"),
                    "end": timezone.localtime(occ.end).strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "course",
                    "location": occ.room.name if occ.room else None,
                }
            )

        return Response(results)
