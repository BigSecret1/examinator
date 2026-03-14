# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "avatar", "date_joined"]
        read_only_fields = ["id", "date_joined"]
