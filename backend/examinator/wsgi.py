# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "examinator.settings.production")

application = get_wsgi_application()
