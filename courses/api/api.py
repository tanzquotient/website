#!/usr/bin/python
# -*- coding: UTF-8 -*-
from rest_framework import generics, permissions

from django.contrib import auth

from .serializers import *

from courses.models import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

class OfferingDetail(generics.RetrieveAPIView):
    model = Offering
    serializer_class = OfferingSerializer
    queryset = Offering.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]


class UserDetail(generics.RetrieveAPIView):
    model = auth.get_user_model()
    serializer_class = UserSerializer
    queryset = auth.get_user_model().objects.all()


class CoursePaymentDetail(generics.RetrieveAPIView):
    model = Course
    serializer_class = CoursePaymentSerializer
    queryset = Course.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]


class SubscriptionPayment(APIView):
    """
    Change if a subscription is payed/not payed
    """
    def get_object(self, pk):
        try:
            return Subscribe.objects.get(pk=pk)
        except Subscribe.DoesNotExist:
            raise Http404

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
