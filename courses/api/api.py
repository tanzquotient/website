from django.contrib import auth
from django.http import Http404
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import *
from .serializers import *
from ..models import Offering, Course, Subscribe, CourseType, Style


class OfferingList(generics.ListAPIView):
    model = Offering
    serializer_class = OfferingSerializer
    queryset = Offering.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class OfferingDetail(generics.RetrieveAPIView):
    model = Offering
    serializer_class = OfferingSerializer
    queryset = Offering.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class UserDetail(generics.RetrieveAPIView):
    model = auth.get_user_model()
    serializer_class = UserSerializer
    queryset = auth.get_user_model().objects.all()
    permission_classes = [permissions.IsAuthenticated]


class CoursePaymentDetail(generics.RetrieveAPIView):
    model = Course
    serializer_class = CoursePaymentSerializer
    queryset = Course.objects.all()
    permission_classes = [TeacherCanReadUpdateCoursePermission]


class SubscriptionPayment(APIView):
    """
    Change if a subscription is paid/not paid
    """

    permission_classes = [TeacherCanReadUpdateSubscriptionPermission]

    def get_object(self, pk):
        try:
            s = Subscribe.objects.get(pk=pk)
        except Subscribe.DoesNotExist:
            raise Http404
        self.check_object_permissions(self.request, s)
        return s

    def get(self, request, pk, format=None):
        s = self.get_object(pk)
        serializer = SubscribePaymentUpdateSerializer(s)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        s = self.get_object(pk)
        serializer = SubscribePaymentUpdateSerializer(s, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseTypeDetail(generics.RetrieveAPIView):
    model = CourseType
    serializer_class = CourseTypeSerializer
    queryset = CourseType.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class StyleDetail(generics.RetrieveAPIView):
    model = Style
    serializer_class = StyleSerializer
    queryset = Style.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class StyleList(generics.ListAPIView):
    model = Style
    serializer_class = StyleSerializer
    queryset = Style.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class FilteredEmailList(generics.ListAPIView):
    model = auth.get_user_model()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = auth.get_user_model().objects.all()

        # get URL arguments
        newsletter = self.request.query_params.get("newsletter", None)
        style_id = self.request.query_params.get("style", None)
        if newsletter is not None and (
            newsletter.lower() == "true" or newsletter.lower() == "false"
        ):
            queryset = queryset.filter(
                subscriptions__user__profile__newsletter=newsletter.lower() == "true"
            )
        if style_id is not None:
            queryset = queryset.filter(subscriptions__course__type__styles=style_id)
        return queryset.distinct()
