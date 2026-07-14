from pydantic import BaseModel, EmailStr


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str


class FcmTokenIn(BaseModel):
    token: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True
