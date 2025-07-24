from pydantic import BaseModel
from typing import List, Optional


class OrderSuccessEmailRequest(BaseModel):
    userName: str
    email: str
    orderId:str


class RegisterSuccessEmailRequest(BaseModel):
    userName: str
    email: str
  