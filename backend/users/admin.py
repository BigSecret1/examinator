from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'google_id', 'created_at')
    search_fields = ('user__email', 'google_id')
    raw_id_fields = ('user',)
