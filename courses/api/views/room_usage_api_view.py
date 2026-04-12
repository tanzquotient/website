from datetime import datetime, time, timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission

from courses.models import LessonOccurrence, Room
from events.models import Event
from django.db.models import Q
from django.urls import reverse


class RoomUsageApiView(APIView):
    """Return lesson occurrences for a room within a given datetime range.

    GET params:
    - room_id: int or list (required)
    - fromDate / from: ISO datetime or YYYY-MM-DD (required)
    - toDate / to: ISO datetime or YYYY-MM-DD (required)
    """

    class _CanViewRoomsCoursesEvents(BasePermission):
        """Allow only users who have both `courses.view_room` and `courses.view_course`."""

        def has_permission(self, request, view):
            user = getattr(request, 'user', None)
            if not user or not user.is_authenticated:
                return False
            return (
                user.has_perm('courses.view_room')
                and user.has_perm('courses.view_course')
                and user.has_perm('events.view_event')
            )

    permission_classes = [_CanViewRoomsCoursesEvents]

    def get(self, request: Request) -> Response:
        # Accept repeated room_id params or a single comma-separated value
        room_ids = request.query_params.getlist("room_id")
        if not room_ids:
            room_param = request.query_params.get("room_id")
            if not room_param:
                return Response(
                    {"detail": "room_id is required"}, status=HTTP_400_BAD_REQUEST
                )
            room_ids = [r.strip() for r in room_param.split(",") if r.strip()]

        try:
            room_ids_int = [int(r) for r in room_ids]
        except ValueError:
            return Response(
                {"detail": "room_id must be integer(s)"}, status=HTTP_400_BAD_REQUEST
            )

        rooms_qs = Room.objects.filter(pk__in=room_ids_int)
        found_ids = set(r.id for r in rooms_qs)
        if len(found_ids) != len(set(room_ids_int)):
            return Response(
                {"detail": "one or more room_id values not found"},
                status=HTTP_400_BAD_REQUEST,
            )

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
            return Response(
                {"detail": "fromDate and toDate are required"},
                status=HTTP_400_BAD_REQUEST,
            )

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
                    return timezone.make_aware(
                        datetime.combine(d, time.max), timezone.get_current_timezone()
                    )
                return timezone.make_aware(
                    datetime.combine(d, time.min), timezone.get_current_timezone()
                )
            return None

        start_dt = _parse(from_str, is_end=False)
        end_dt = _parse(to_str, is_end=True)

        if not start_dt or not end_dt:
            return Response(
                {"detail": "Could not parse fromDate/toDate"},
                status=HTTP_400_BAD_REQUEST,
            )

        # Handle cases where the client provides the same date/time for from/to
        # (common when a UI passes midnight datetimes for a single-day view).
        # If end is not after start but they fall on the same date, treat end
        # as the end of that day to make the range inclusive for that day.
        if end_dt <= start_dt:
            if start_dt.date() == end_dt.date():
                end_dt = timezone.make_aware(
                    datetime.combine(end_dt.date(), time.max),
                    timezone.get_current_timezone(),
                )
            else:
                # If end is before start across dates, try extending end to its day's end
                # if that makes it after start; otherwise swap to avoid empty result.
                end_of_end_day = timezone.make_aware(
                    datetime.combine(end_dt.date(), time.max),
                    timezone.get_current_timezone(),
                )
                if end_of_end_day >= start_dt:
                    end_dt = end_of_end_day
                else:
                    tmp = start_dt
                    start_dt = end_dt
                    end_dt = tmp

        # include events from the Event model (explicit events assigned to rooms)
        # and occurrences where the lesson.room is None but the course's room matches (course)
        # Event objects use date/time fields; compute their datetimes in Python and
        # include those that overlap the requested interval.

        results = []

        # Events
        start_date = start_dt.date()
        end_date = end_dt.date()

        events_qs = (
            Event.objects.filter(room__in=room_ids_int)
            .filter(date__lte=end_date)
            .filter(
                Q(date_to__gte=start_date)
                | Q(date_to__isnull=True, date__gte=start_date)
            )
            .order_by("date")
            .all()
        )

        for ev in events_qs:
            # compute event start/end datetimes similar to events.ical.EventFeed
            event_start = (
                timezone.make_aware(
                    datetime.combine(ev.date, ev.time_from or time.min),
                    timezone.get_current_timezone(),
                )
                if ev.time_from is not None
                else timezone.make_aware(
                    datetime.combine(ev.date, time.min), timezone.get_current_timezone()
                )
            )

            date_to = ev.date_to or ev.date
            event_end = (
                timezone.make_aware(
                    datetime.combine(date_to, ev.time_to),
                    timezone.get_current_timezone(),
                )
                if ev.time_to is not None
                else timezone.make_aware(
                    datetime.combine(date_to + timedelta(days=1), time.min),
                    timezone.get_current_timezone(),
                )
            )

            # include only if overlaps requested interval
            if event_end >= start_dt and event_start <= end_dt:
                results.append(
                    {
                        "id": ev.id,
                        "title": ev.get_name() if hasattr(ev, "get_name") else str(ev),
                        "start": timezone.localtime(event_start).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "end": timezone.localtime(event_end).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "type": "event",
                        "location": ev.room.name if ev.room else None,
                        # Provide canonical URLs for frontend use
                        "public_url": reverse("events:detail", args=[ev.id]),
                        "admin_url": f"/admin/events/event/{ev.id}/change/",
                    }
                )

        # Lesson occurrences (courses)
        occurrences = (
            LessonOccurrence.objects.select_related("course", "room", "course__type")
            .filter(
                (
                    Q(room__in=room_ids_int)
                    | (Q(room__isnull=True) & Q(course__room__in=room_ids_int))
                ),
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
                    "title": occ.course.name,
                    "start": timezone.localtime(occ.start).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "end": timezone.localtime(occ.end).strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "course",
                    "location": occ.room.name if occ.room else None,
                    # Provide canonical URLs for frontend use
                    "public_url": reverse(
                        "courses:course_detail", args=[occ.course.id]
                    ),
                    "admin_url": f"/admin/courses/course/{occ.course.id}/change/",
                }
            )

        return Response(results)
