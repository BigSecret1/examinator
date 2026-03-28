from .actions import GeminiClientAction


class GeminiClientInterface:
    """Public interface for other apps to interact with the Gemini client. """

    @staticmethod
    def generate(system_instruction, response_schema, prompt, **kwargs):
        """Generate structured JSON content from Gemini.

        Args:
            system_instruction: System-level instruction for the model.
            response_schema: JSON schema the model must conform to.
            prompt: The user prompt to send.
            **kwargs: Optional overrides passed to GeminiClientAction
                (temperature, models, max_retries).

        Returns:
            dict: Parsed JSON response from Gemini.
        """
        client = GeminiClientAction(
            system_instruction=system_instruction,
            response_schema=response_schema,
            **kwargs,
        )
        return client.generate(prompt)
