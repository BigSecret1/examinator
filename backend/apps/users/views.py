# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from rest_framework import generics, permissions

from .models import User
from .serializers import UserSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
