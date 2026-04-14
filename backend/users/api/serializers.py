from rest_framework import serializers

from ..models import User


class GoogleLoginSerializer(serializers.Serializer):
    credential = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar_url',
            'date_joined',
        ]
        read_only_fields = fields
