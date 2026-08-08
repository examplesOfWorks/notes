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

@app.get("/notes")
def read_notes(search: str | None = None, limit: int | None = None):
    result = notes
    if search:
        result = [note for note in result if search.lower() in note["title"].lower()]
    if limit is not None and limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be positive")
    if limit is not None:
        result = result[:limit]
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
    last_id = notes[-1]["id"]
    new_note["id"] = last_id + 1
    notes.append(new_note)
    return new_note

@app.put("/notes/{note_id}")
def update_note(note_id: int, note: NoteCreate):
    for existing_note in notes:
        if existing_note["id"] == note_id:
            existing_note["title"] = note.title
            existing_note["text"] = note.text
            return existing_note

    raise HTTPException(status_code=404, detail="Note not found")

@app.patch("/notes/{note_id}")
def patch_note(note_id: int, note: NoteUpdate):
    update_note = note.model_dump(exclude_unset=True)

    for existing_note in notes:
        if existing_note["id"] == note_id:
            if "title" in update_note:
                existing_note["title"] = update_note["title"]
            if "text" in update_note:
                existing_note["text"] = update_note["text"]

            return existing_note

    raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    for note in notes:
        if note["id"] == note_id:
            notes.remove(note)
            return "Note deleted"
    raise HTTPException(status_code=404, detail="Note not found")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)