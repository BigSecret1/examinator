# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.contrib import admin

from .models import (
    Feedback,
    FileUploadActivity,
    FileUploadDailyUsage,
    Note,
    NoteFlashcard,
    NoteKeyTerm,
    NoteSection,
    NoteSubtopic,
    UserUploadQuota,
)


class NoteSubtopicInline(admin.TabularInline):
    model = NoteSubtopic
    extra = 0
    fields = ('position', 'heading')
    ordering = ('position',)


@admin.register(NoteSection)
class NoteSectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'note', 'position', 'heading')
    list_filter = ('note',)
    search_fields = ('heading',)
    inlines = [NoteSubtopicInline]


class NoteFlashcardInline(admin.TabularInline):
    model = NoteFlashcard
    extra = 0
    fields = ('position', 'question')
    ordering = ('position',)


class NoteKeyTermInline(admin.TabularInline):
    model = NoteKeyTerm
    extra = 0
    fields = ('position', 'term', 'definition')
    ordering = ('position',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'user', 'status',
        'generation_mode', 'page_count', 'created_at',
    )
    list_filter = ('status', 'generation_mode')
    search_fields = ('title', 'source_filename', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [NoteKeyTermInline, NoteFlashcardInline]


@admin.register(FileUploadActivity)
class FileUploadActivityAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'purpose', 'file_name', 'file_size',
        'page_count', 'status', 'rejection_reason', 'created_at',
    )
    list_filter = ('status', 'purpose', 'rejection_reason')
    search_fields = ('file_name', 'user__email')
    readonly_fields = ('created_at',)


@admin.register(FileUploadDailyUsage)
class FileUploadDailyUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'count', 'updated_at')
    list_filter = ('date',)
    search_fields = ('user__email',)


@admin.register(UserUploadQuota)
class UserUploadQuotaAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'daily_limit', 'updated_at')
    list_filter = ('tier',)
    search_fields = ('user__email', 'note')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'note', 'rating', 'short_message', 'created_at')
    list_filter = ('rating',)
    search_fields = ('message', 'user__email')
    readonly_fields = ('created_at',)

    def short_message(self, obj):
        return obj.message[:80]
    short_message.short_description = 'Message'

