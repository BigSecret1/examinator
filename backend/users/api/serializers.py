from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class GoogleLoginSerializer(serializers.Serializer):
    credential = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.CharField(
            source='profile.avatar_url',
            default='',
            read_only=True,
    )

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
