"""AI Coding Assistant — streamed, code-focused prompting."""
from app.services import llm

SYSTEM = (
    "You are a senior software engineer. Provide correct, idiomatic code with brief "
    "explanations. Point out bugs, edge cases, and complexity. Use markdown code blocks."
)


async def assist(task: str, code: str = "", language: str = ""):
    user = task
    if code:
        user += f"\n\n```{language}\n{code}\n```"
    async for token in llm.stream_chat([("system", SYSTEM), ("user", user)], temperature=0.1):
        yield token
