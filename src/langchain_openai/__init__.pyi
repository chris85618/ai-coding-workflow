class ChatOpenAI:
    def __init__(
        self,
        model: str,
        temperature: float,
        max_tokens: int | None = ...,
        openai_api_key: str | None = ...,
        base_url: str | None = ...,
    ) -> None: ...
