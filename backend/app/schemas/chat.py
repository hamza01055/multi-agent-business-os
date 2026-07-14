from pydantic import BaseModel


class ConversationCreate(BaseModel):
    workspace_id: str
    title: str = "New chat"
    kind: str = "chat"


class MessageIn(BaseModel):
    content: str
    stream: bool = True


class MessageOut(BaseModel):
    id: str
    role: str
    content: str

    class Config:
        from_attributes = True


class ChatQuestion(BaseModel):
    question: str
