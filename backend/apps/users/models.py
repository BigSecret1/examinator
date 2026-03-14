# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model for Examinator."""

    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
