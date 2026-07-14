from pydantic import BaseModel, HttpUrl, Field


class WebsiteIngestIn(BaseModel):
    workspace_id: str
    url: HttpUrl
    max_pages: int = Field(default=5, le=25)


class YouTubeIngestIn(BaseModel):
    workspace_id: str
    video_url: str


class EmailDraftIn(BaseModel):
    intent: str                      # what the email should accomplish
    context: str = ""                # thread / background
    tone: str = "professional"       # professional | friendly | direct
    variants: int = Field(default=1, le=3)


class EmailDraftOut(BaseModel):
    subject: str
    body: str


class ResearchIn(BaseModel):
    workspace_id: str
    question: str
    depth: int = Field(default=2, le=4)


class ReportIn(BaseModel):
    workspace_id: str
    topic: str
    template: str = "executive"      # executive | technical | marketing
    document_ids: list[str] = Field(default_factory=list)


class CodingIn(BaseModel):
    task: str
    code: str = ""
    language: str = ""


class WorkflowIn(BaseModel):
    workspace_id: str
    task: str


class KBArticleIn(BaseModel):
    workspace_id: str
    title: str
    content: str
