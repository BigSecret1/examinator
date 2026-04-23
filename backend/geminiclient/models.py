from django.db import models


class GeminiAPICall(models.Model):
    model_name = models.CharField(max_length=100)
    caller = models.CharField(
        max_length=100,
        blank=True,
        help_text='Feature or task that triggered this call (e.g. exam_questions).',
    )
    input_tokens = models.PositiveIntegerField()
    output_tokens = models.PositiveIntegerField()
    input_cost_usd = models.DecimalField(max_digits=12, decimal_places=8)
    output_cost_usd = models.DecimalField(max_digits=12, decimal_places=8)
    total_cost_usd = models.DecimalField(max_digits=12, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'examinator_gemini_api_call'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.model_name} | {self.total_cost_usd} USD | {self.created_at:%Y-%m-%d %H:%M}'

