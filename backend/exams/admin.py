from django.contrib import admin

from .models import Exam, ExamQuestion, ExamQuestionAnswer


class ExamQuestionAnswerInline(admin.TabularInline):
    model = ExamQuestionAnswer
    extra = 0


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'conducting_body', 'is_active')
    list_filter = ('is_active', 'country')
    search_fields = ('name', 'conducting_body')


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'exam', 'subject', 'difficulty', 'created_at')
    list_filter = ('exam', 'difficulty')
    search_fields = ('text',)
    inlines = [ExamQuestionAnswerInline]

    def text_short(self, obj):
        return obj.text[:80]
    text_short.short_description = 'Question'
