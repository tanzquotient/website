from rest_framework import serializers

from courses.api.serializers.user_serializer import UserSerializer
from courses.models import Subscribe


class SubscribePaymentSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()
    partner = serializers.StringRelatedField()
    price_to_pay = serializers.DecimalField(
        source="price_to_pay", decimal_places=2, max_digits=6
    )
    detail = serializers.HyperlinkedIdentityField(
        view_name="courses:api:subscription-payment"
    )

    class Meta:
        model = Subscribe
        fields = ("id", "user", "partner", "price_to_pay", "payed", "detail")
