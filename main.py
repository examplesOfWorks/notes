from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field

app = FastAPI()


notes = [
    {
        "id": 1,
        "title": "Изучить FastAPI",
        "text": "Разобраться с эндпоинтами"
    },
    {
        "id": 2,
        "title": "Изучить Pydantic",
        "text": "Разобраться с валидацией"
    }
]

class NoteCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100
    )
    text: str = Field(
        min_length=1,
        max_length=5000
    )

@app.get("/notes")
def read_notes(search: str | None = None, limit: int | None = None):
    result = notes
    if search:
        result = [note for note in notes if search.lower() in note["title"].lower()]
    if limit is not None:
        result = result[:limit]
    if limit is not None and limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be positive")
    return result

@app.get("/notes/{note_id}")
def read_note(note_id: int):
    for note in notes:
        if note["id"] == note_id:
            return note
    raise HTTPException(status_code=404, detail="Note not found")
        
@app.post("/notes")
def create_note(note: NoteCreate):
    new_note = note.model_dump()
    new_note["id"] = len(notes) + 1
    notes.append(new_note)
    return new_note


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)