from pydantic import BaseModel


class TagModel(BaseModel):
    name: str

class TagUpdateModel(BaseModel):
    tags: list[str]