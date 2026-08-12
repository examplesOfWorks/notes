from pydantic import BaseModel, Field


class NoteResponse(BaseModel):
    id: int
    title: str = Field(
        min_length=1,
        max_length=100
    )
    text: str = Field(
        min_length=1,
        max_length=5000
    )
    image: str | None = None

class NoteCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100
    )
    text: str = Field(
        min_length=1,
        max_length=5000
    )


class NoteUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )
    text: str | None = Field(
        default=None,
        min_length=1,
        max_length=5000
    )
