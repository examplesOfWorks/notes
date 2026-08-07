from fastapi import FastAPI, HTTPException
import uvicorn

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

@app.get("/notes")
def read_notes(search: str | None = None, limit: int | None = None):
    if search:
        result = [note for note in notes if search.lower() in note["title"].lower()]
    if limit:
        result = result[:limit]
    return result

@app.get("/notes/{note_id}")
def read_note(note_id: int):
    for note in notes:
        if note["id"] == note_id:
            return note
    return "Note not found"
        



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)