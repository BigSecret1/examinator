# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.contrib import admin

from .models import Subject, Topic

admin.site.register(Subject)
admin.site.register(Topic)
