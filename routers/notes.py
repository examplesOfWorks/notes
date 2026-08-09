from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ValidationError
import json

router = APIRouter(
    prefix="/notes",
    tags=["Заметки"],
)

path_to_file = "notes.json"
    

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

            if not isinstance(data, list):
                raise HTTPException(
                    status_code=500,
                    detail="JSON должен содержать список заметок"
                )

            return [Note(**note) for note in data]
        
    except FileNotFoundError:
        return []
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Файл JSON поврежден"
        )
    
    except ValidationError:
        raise HTTPException(
            status_code=500,
            detail="Данные хранятся в неправильном формате"
        )
 
def write_file(path, data):
    data = [note.model_dump() for note in data]
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

class Note(BaseModel):
    id: int
    title: str = Field(
        min_length=1,
        max_length=100
    )
    text: str = Field(
        min_length=1,
        max_length=5000
    )

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

@router.get("/", response_model=list[Note])
def read_notes(search: str | None = None, limit: int | None = None):
    notes = read_file(path_to_file)
    result = notes

    if search:
        result = [note for note in result if search.lower() in note.title.lower()]
    if limit is not None and limit < 1:
        raise HTTPException(status_code=400, detail="Число должно быть больше 0")
    if limit is not None:
        result = result[:limit]

    return result

@router.get("/{note_id}", response_model=Note)
def read_note(note_id: int):
    notes = read_file(path_to_file)

    for note in notes:
        if note.id == note_id:
            return note
        
    raise HTTPException(status_code=404, detail="Заметка не найдена")
        
@router.post("/", response_model=Note)
def create_note(note: NoteCreate):
    notes = read_file(path_to_file)

    try:
        last_id = notes[-1].id
    except IndexError:
        last_id = 0

    new_note = Note(
        id=last_id + 1,
        title=note.title,
        text=note.text
    )
    
    notes.append(new_note)
    write_file(path_to_file, notes)

    return new_note

@router.put("/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteCreate):
    notes = read_file(path_to_file)

    for existing_note in notes:
        if existing_note.id == note_id:
            existing_note.title = note.title
            existing_note.text = note.text
            write_file(path_to_file, notes)
            return existing_note

    raise HTTPException(status_code=404, detail="Заметка не найдена")

@router.patch("/{note_id}", response_model=Note)
def patch_note(note_id: int, note: NoteUpdate):
    notes = read_file(path_to_file)
    update_note = note.model_dump(exclude_unset=True)

    for existing_note in notes:
        if existing_note.id == note_id:
            if "title" in update_note:
                existing_note.title = update_note.title
            if "text" in update_note:
                existing_note.text = update_note.text
            
            write_file(path_to_file, notes)
            return existing_note

    raise HTTPException(status_code=404, detail="Заметка не найдена")

@router.delete("/{note_id}")
def delete_note(note_id: int):
    notes = read_file(path_to_file)

    for note in notes:
        if note.id == note_id:
            notes.remove(note)
            write_file(path_to_file, notes)
            return {"message": "Заметка удалена"}
        
    raise HTTPException(status_code=404, detail="Заметка не найдена")