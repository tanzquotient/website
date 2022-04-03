from rest_framework import serializers

from django.contrib import auth

from courses.models import *


class OfferingSerializer(serializers.HyperlinkedModelSerializer):
    course_set = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='courses:api:course-payment-detail')
    period = serializers.StringRelatedField()

    class Meta:
        model = Offering
        fields = ('id', 'name', 'period', 'course_set')


class UserSerializer(serializers.ModelSerializer):
    student_status = serializers.StringRelatedField(source='profile.student_status')

    class Meta:
        model = auth.get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'student_status')


class SubscribePaymentSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()
    partner = serializers.StringRelatedField()
    price_to_pay = serializers.DecimalField(source='price_to_pay', decimal_places=2, max_digits=6)
    detail = serializers.HyperlinkedIdentityField(view_name='courses:api:subscription-payment')

    class Meta:
        model = Subscribe
        fields = ('id', 'user', 'partner', 'price_to_pay', 'payed', 'detail')


class CoursePaymentSerializer(serializers.HyperlinkedModelSerializer):
    offering = serializers.HyperlinkedRelatedField(view_name='courses:api:offering-detail', read_only=True)
    type_name = serializers.StringRelatedField(source='type')
    type = serializers.HyperlinkedRelatedField(view_name='courses:api:coursetype-detail', read_only=True)
    # this calls the method participatory() and serializes the returned queryset
    participatory = SubscribePaymentSerializer(many=True)

    class Meta:
        model = Course
        fields = ('id', 'name', 'type_name', 'type', 'offering', 'participatory')


class SubscribePaymentUpdateSerializer(serializers.Serializer):
    paid = serializers.BooleanField()

    def update(self, instance, validated_data):
        instance.paid = validated_data.get('paid', instance.paid)
        instance.save()
        return instance


class CourseTypeSerializer(serializers.HyperlinkedModelSerializer):
    styles = serializers.HyperlinkedRelatedField(many=True, view_name='courses:api:style-detail', read_only=True)

    class Meta:
        model = CourseType
        fields = ('name', 'styles', 'level', 'couple_course')


class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
