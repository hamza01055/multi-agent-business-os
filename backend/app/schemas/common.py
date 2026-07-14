from pydantic import BaseModel


class JobOut(BaseModel):
    job_id: str
    status: str = "pending"


class Msg(BaseModel):
    detail: str
