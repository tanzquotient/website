from rest_framework.serializers import ModelSerializer

from ...models import Subscribe


class ChooseRoleSerializer(ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ["course", "lead_follow"]
