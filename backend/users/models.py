from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='profile',
    )
    google_id = models.CharField(max_length=255, unique=True)
    avatar_url = models.URLField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'examinator_users_profile'

    def __str__(self):
        return self.user.email
