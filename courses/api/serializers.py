#!/usr/bin/python
# -*- coding: UTF-8 -*-
from rest_framework import serializers

from django.contrib import auth

from courses.models import *


class OfferingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offering
        fields = ('id', 'name',)


class UserSerializer(serializers.ModelSerializer):
    student_status = serializers.StringRelatedField(source='profile.student_status')

    class Meta:
        model = auth.get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'student_status')


class SubscribePaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    partner = serializers.StringRelatedField()
    price_to_pay = serializers.FloatField(source='get_price_to_pay')

    class Meta:
        model = Subscribe
        fields = ('id', 'user', 'partner', 'price_to_pay', 'payed')


class CoursePaymentSerializer(serializers.HyperlinkedModelSerializer):
    offering = serializers.HyperlinkedRelatedField(view_name='courses:offering-detail', read_only=True)
    type = serializers.StringRelatedField()
    # this calls the method participatory() and serializes the returned queryset
    participatory = SubscribePaymentSerializer(many=True)

    class Meta:
        model = Course
        fields = ('id', 'name', 'type', 'offering', 'participatory',)


class SubscribePaymentUpdateSerializer(serializers.Serializer):
    payed = serializers.BooleanField()

    def update(self, instance, validated_data):
        print "update with {}".format(validated_data.get('payed', instance.payed))
        instance.payed = validated_data.get('payed', instance.payed)
        instance.save()
        return instance