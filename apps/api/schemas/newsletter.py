from datetime import datetime

from pydantic import BaseModel, EmailStr


class SubscribeResponse(BaseModel):
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}


class SubscribeRequest(BaseModel):
    email: EmailStr


class UnsubscribeRequest(BaseModel):
    email: EmailStr


class UnsubscribeResponse(BaseModel):
    message: str
