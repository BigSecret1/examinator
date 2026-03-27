from django.contrib import admin

from .models import Exam


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'conducting_body', 'is_active')
    list_filter = ('is_active', 'country')
    search_fields = ('name', 'conducting_body')
