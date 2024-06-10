from rest_framework import serializers


class SubscribePaymentUpdateSerializer(serializers.Serializer):
    paid = serializers.BooleanField()

    def update(self, instance, validated_data):
        instance.paid = validated_data.get("paid", instance.paid)
        instance.save()
        return instance
