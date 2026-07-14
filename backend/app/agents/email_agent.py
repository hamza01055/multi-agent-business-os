"""Email Assistant — drafting and replying with tone control."""
from app.services.llm import complete


async def draft_email(intent: str, context: str, tone: str) -> dict:
    content = await complete([
        ("system",
         f"You draft business emails in a {tone} tone. "
         "Return the subject on the first line prefixed 'Subject: ', then a blank line, then the body. "
         "Be concise; no placeholders left unfilled unless unavoidable."),
        ("user", f"Goal: {intent}\n\nBackground/thread:\n{context or '(none)'}"),
    ])
    lines = content.splitlines()
    subject = lines[0].removeprefix("Subject:").strip() if lines else ""
    body = "\n".join(lines[1:]).strip()
    return {"subject": subject, "body": body}


async def reply_email(thread: str, instruction: str) -> dict:
    content = await complete([
        ("system", "Write a reply to the email thread following the user's instruction. "
                   "First line: 'Subject: Re: ...', then blank line, then body."),
        ("user", f"Thread:\n{thread}\n\nInstruction: {instruction}"),
    ])
    lines = content.splitlines()
    return {"subject": lines[0].removeprefix("Subject:").strip() if lines else "",
            "body": "\n".join(lines[1:]).strip()}
