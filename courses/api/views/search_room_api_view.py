from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Room


class SearchRoomApiView(APIView):
    class _CanViewRoomsAndCourses(BasePermission):
        """Allow only users who have both `courses.view_room` and `courses.view_course`."""

        def has_permission(self, request, view):
            user = getattr(request, "user", None)
            if not user or not user.is_authenticated:
                return False
            return (
                user.has_perm("courses.view_room")
                and user.has_perm("courses.view_course")
                and user.has_perm("events.view_event")
            )

    permission_classes = [_CanViewRoomsAndCourses]

    def get(self, request: Request) -> Response:
        room_id = (request.query_params.get("id") or "").strip()
        if room_id:
            try:
                room = Room.objects.get(pk=int(room_id))
                return Response([{"value": room.id, "text": room.name}])
            except Room.DoesNotExist, ValueError:
                return Response([], status=200)

        q = (request.query_params.get("q") or "").strip()
        try:
            limit = int(request.query_params.get("limit", "20").strip())
        except Exception:
            limit = 20

        if not q:
            return Response([], status=200)

        rooms_qs = Room.objects.filter(name__icontains=q).order_by("name")[:limit]
        results = [{"value": r.id, "text": r.name} for r in rooms_qs]
        return Response(results)
