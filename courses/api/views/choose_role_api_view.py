from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from ..serializers import ChooseRoleSerializer
from ...models import Course, LeadFollow, Subscribe, SubscribeState


class ChooseRoleApiView(APIView):

    def post(self, request: Request) -> Response:
        serializer = ChooseRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

        user = request.user
        role = serializer.data["lead_follow"]
        course = get_object_or_404(Course, pk=serializer.data["course"])

        if role == LeadFollow.NO_PREFERENCE:
            raise ValidationError(detail="You need to choose a role.")

        subscription: Subscribe = get_object_or_404(
            Subscribe,
            course=course,
            user=user,
            state__in=SubscribeState.ACCEPTED_STATES,
        )

        if subscription.lead_follow != LeadFollow.NO_PREFERENCE:
            raise ValidationError(
                detail="Your role has already been set. You can not change it anymore."
            )

        subscription.lead_follow = role
        subscription.save()

        return Response(data=ChooseRoleSerializer(instance=subscription).data)
