from .actions import GeminiClientAction


class GeminiClientInterface:

    @staticmethod
    def generate(system_instruction, response_schema, prompt, caller='', **kwargs):
        client = GeminiClientAction(
            system_instruction=system_instruction,
            response_schema=response_schema,
            caller=caller,
            **kwargs,
        )
        return client.generate(prompt)
