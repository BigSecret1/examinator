from .actions import GeminiClientAction


class GeminiClientInterface:

    @staticmethod
    def generate(
            system_instruction,
            response_schema,
            prompt,
            caller='',
            inline_files=None,
            **kwargs,
    ):
        '''Generate a structured response from Gemini.

        Args:
            system_instruction: System instruction text.
            response_schema: JSON schema dict for structured output.
            prompt: The text prompt.
            caller: Optional caller identifier for cost logging.
            inline_files: Optional list of (mime_type, bytes) tuples for
                multimodal inputs (e.g. PDFs, images). Each tuple becomes
                an inline data part sent alongside the prompt.
            **kwargs: Forwarded to GeminiClientAction (e.g. temperature,
                max_output_tokens, models, max_retries).
        '''
        client = GeminiClientAction(
            system_instruction=system_instruction,
            response_schema=response_schema,
            caller=caller,
            **kwargs,
        )
        return client.generate(prompt, inline_files=inline_files)
