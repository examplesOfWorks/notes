from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse


from models import Note
from schemas.note import NoteResponse, NoteCreate, NoteUpdate
from services.image_service import upload_image, delete_image, PATH_TO_IMAGES

from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_session


router = APIRouter(
    prefix="/notes",
    tags=["Заметки"],
)


@router.get("/", response_model=list[NoteResponse])
def read_notes(
    search: str | None = None,
    limit: int | None = None,
    session: Session = Depends(get_session)
):
    
    statement = select(Note)

    if search:
        statement = statement.where(Note.title.ilike(f"%{search}%"))
    if limit is not None and limit < 1:
        raise HTTPException(status_code=400, detail="Число должно быть больше 0")
    if limit is not None:
        statement = statement.limit(limit)

    notes = session.scalars(statement).all()

    return notes

@router.get("/{note_id}", response_model=NoteResponse)
def read_note(
    note_id: int,
    session: Session = Depends(get_session)
):

    note = session.get(Note, note_id)

    if note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    
    return note
        

@router.get("/{note_id}/image")
def get_note_image(
    note_id: int,
    session: Session = Depends(get_session)
):

    note = session.get(Note, note_id)

    if note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")


    if note.image is None:
        raise HTTPException(
            status_code=404,
            detail="У заметки нет изображения"
        )
            
    path = PATH_TO_IMAGES / note.image

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Файл изображения не найден"
        )

    return FileResponse(path)
          
        
@router.post("/", response_model=NoteResponse)
def create_note(
    title: str = Form(...),
    text: str = Form(...),
    image: UploadFile | None = None,
    session: Session = Depends(get_session)
):

    note = NoteCreate(title=title, text=text)

    image_name = None

    if image:
        image_name = upload_image(image)

    new_note = Note(
        title=note.title,
        text=note.text,
        image=image_name
    )

    session.add(new_note)
    session.commit()
    session.refresh(new_note)

    return new_note

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(note_id: int,
    title: str = Form(...),
    text: str = Form(...),
    image: UploadFile | None = None,
    session: Session = Depends(get_session)
):

    note = NoteCreate(title=title, text=text)

    existing_note = session.get(Note, note_id)

    if existing_note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    existing_note.title = note.title
    existing_note.text = note.text

    if existing_note.image is not None:
        delete_image(existing_note.image)
        existing_note.image = None

    if image:
        image_name = upload_image(image)
        existing_note.image = image_name
            
    session.commit()
    return existing_note


@router.patch("/{note_id}", response_model=NoteResponse)
def patch_note(note_id: int, 
    title: str | None = Form(default=None),
    text: str | None = Form(default=None),
    image : UploadFile | None = None,
    session: Session = Depends(get_session)
):
    
    note = NoteUpdate(title=title, text=text)

    existing_note = session.get(Note, note_id)

    if existing_note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    if title is not None:
        existing_note.title = note.title

    if text is not None:
        existing_note.text = note.text

    if image:
        if existing_note.image is not None:
            delete_image(existing_note.image)

        image_name = upload_image(image)
        existing_note.image = image_name
            
    session.commit()
    return existing_note


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    session: Session = Depends(get_session)
):

    note = session.get(Note, note_id)

    if note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    if note.image is not None:
        delete_image(note.image)

    session.delete(note)
    session.commit()

    return {"message": "Заметка удалена"}
        

@router.delete("/{note_id}/image")
def delete_note_image(
    note_id: int,
    session: Session = Depends(get_session)
):

    note = session.get(Note, note_id)

    if note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    if note.image is None:
        raise HTTPException(
            status_code=404,
            detail="У заметки нет изображения"
        )
            
    delete_image(note.image)
    note.image = None

    session.commit()

    return {"message": "Изображение удалено"}
