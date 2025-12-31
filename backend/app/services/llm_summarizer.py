from typing import List, Optional
def summarize_insights(insights: List[dict]) -> Optional[str]:
    return "Temporarily disabled summarization"
    # client = _get_client()
    # if client is None or not insights:
    #     return None

    # insight_text = "\n".join(
    #     f"- {item['message']}" for item in insights if "message" in item
    # )

    # prompt = _build_prompt(insight_text)

    # try:
    #     response = client.chat(
    #         model=settings.COHERE_MODEL or "command-r",
    #         message=prompt,
    #         temperature=0.3,
    #         max_tokens=120,
    #     )
    #     print("Cohere summarization response:", response.text)
    #     return response.text.strip() if response.text else None

    # except Exception as exc:
    #     # Graceful degradation (dashboard still works)
    #     print("Cohere summarization failed:", exc)
    #     return None


def _build_prompt(insight_text: str) -> str:
    return (
        "You are a data analyst assistant.\n"
        "Summarize the following analytical insights in a concise, "
        "professional tone suitable for a business dashboard.\n"
        "Do not introduce new facts or assumptions.\n\n"
        "Insights:\n"
        f"{insight_text}\n\n"
        "Summary (2–3 sentences):"
    )


def _get_client() -> Optional[cohere.Client]:
    global _client

    if not settings.COHERE_API_KEY:
        return None

    if _client is None:
        _client = cohere.Client(settings.COHERE_API_KEY)

    return _client
