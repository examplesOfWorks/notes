from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ValidationError
import json
from pathlib import Path
from uuid import uuid4

router = APIRouter(
    prefix="/notes",
    tags=["Заметки"],
)

path_to_file = "notes.json"
    
path_to_images = Path("images")
path_to_images.mkdir(exist_ok=True)


def upload_image(file: UploadFile):
    if file.content_type not in {
        "image/jpeg",
        "image/png"
    }:
        raise HTTPException(
            status_code=400,
            detail="Файл должен быть JPEG или PNG"
        )
    
    extention = ".jpg" if file.content_type == "image/jpeg" else ".png"
    file.filename = f"{uuid4()}.{extention}"

    path = path_to_images / file.filename

    with open(path, "wb") as buffer:
        buffer.write(file.file.read())

    return file.filename


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

@router.get("/{note_id}/image")
def get_note_image(note_id: int):
    notes = read_file(path_to_file)

    for note in notes:
        if note.id == note_id:

            if note.image is None:
                raise HTTPException(
                    status_code=404,
                    detail="У заметки нет изображения"
                )
            
            path = path_to_images / note.image

            if not path.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Файл изображения не найден"
                )

            return FileResponse(path)
        
    raise HTTPException(status_code=404, detail="Заметка не найдена")
        
@router.post("/", response_model=Note)
def create_note(
    title: str = Form(...),
    text: str = Form(...),
    image: UploadFile | None = None
):

    note = NoteCreate(title=title, text=text)

    notes = read_file(path_to_file)

    try:
        last_id = notes[-1].id
    except IndexError:
        last_id = 0

    image_name = None

    if image:
        image_name = upload_image(image)

    new_note = Note(
        id=last_id + 1,
        title=note.title,
        text=note.text,
        image=image_name
    )
    
    notes.append(new_note)
    write_file(path_to_file, notes)

    return new_note

@router.put("/{note_id}", response_model=Note)
def update_note(note_id: int,
    title: str = Form(...),
    text: str = Form(...),
    image: UploadFile | None = None
):

    note = NoteCreate(title=title, text=text)

    notes = read_file(path_to_file)

    image_name = None

    for existing_note in notes:
        if existing_note.id == note_id:
            existing_note.title = note.title
            existing_note.text = note.text
            if existing_note.image is not None:
                path = path_to_images / existing_note.image
                if path.exists():
                    path.unlink()
                existing_note.image = None
            if image:
                image_name = upload_image(image)
                existing_note.image = image_name
            
            write_file(path_to_file, notes)
            return existing_note

    raise HTTPException(status_code=404, detail="Заметка не найдена")

@router.patch("/{note_id}", response_model=Note)
def patch_note(note_id: int, 
    title: str | None = Form(default=None),
    text: str | None = Form(default=None),
    image : UploadFile | None = None
):
    
    note = NoteUpdate(title=title, text=text)

    notes = read_file(path_to_file)

    image_name = None

    for existing_note in notes:
        if existing_note.id == note_id:

            if title is not None:
                existing_note.title = note.title
            if text is not None:
                existing_note.text = note.text
            if image:
                if existing_note.image is not None:
                    path = path_to_images / existing_note.image
                    if path.exists():
                        path.unlink()
                image_name = upload_image(image)
                existing_note.image = image_name
            
            write_file(path_to_file, notes)
            return existing_note

    raise HTTPException(status_code=404, detail="Заметка не найдена")

@router.delete("/{note_id}")
def delete_note(note_id: int):
    notes = read_file(path_to_file)

    for note in notes:
        if note.id == note_id:
            if note.image is not None:
                path = path_to_images / note.image
                if path.exists():
                    path.unlink()
            notes.remove(note)
            write_file(path_to_file, notes)
            return {"message": "Заметка удалена"}
        
    raise HTTPException(status_code=404, detail="Заметка не найдена")

@router.delete("/{note_id}/image")
def delete_note_image(note_id: int):
    notes = read_file(path_to_file)

    for note in notes:
        if note.id == note_id:

            if note.image is None:
                raise HTTPException(
                    status_code=404,
                    detail="У заметки нет изображения"
                )
            
            path = path_to_images / note.image

            if not path.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Файл изображения не найден"
                )
            
            path.unlink()
            note.image = None
            write_file(path_to_file, notes)

            return {"message": "Изображение удалено"}
        
    raise HTTPException(status_code=404, detail="Заметка не найдена")

