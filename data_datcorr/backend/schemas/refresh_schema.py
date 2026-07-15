from pydantic import BaseModel


class RefreshRequest(BaseModel):

    refresh_token: str


class RefreshResponse(BaseModel):

    success: bool

    access_token: str

    token_type: str = "bearer"