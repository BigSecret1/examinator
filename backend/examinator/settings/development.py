# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0
#
# Development settings – never use in production.

from decouple import config

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="examinator"),
        "USER": config("DB_USER", default="examinator"),
        "PASSWORD": config("DB_PASSWORD", default="examinator"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}
