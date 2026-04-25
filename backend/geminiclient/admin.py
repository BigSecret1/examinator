from django.contrib import admin

from .models import GeminiAPICall


@admin.register(GeminiAPICall)
class GeminiAPICallAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'model_name', 'caller',
        'input_tokens', 'output_tokens',
        'input_cost_usd', 'output_cost_usd', 'total_cost_usd',
    ]
    list_filter = ['model_name', 'caller']
    readonly_fields = [
        'model_name', 'caller', 'input_tokens', 'output_tokens',
        'input_cost_usd', 'output_cost_usd', 'total_cost_usd', 'created_at',
    ]
