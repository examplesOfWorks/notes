from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse


from models import Note
from schemas.note import NoteResponse, NoteCreate, NoteUpdate

from services.image_service import upload_image, delete_image, PATH_TO_IMAGES

from dependencies import CurrentNote, CurrentUser, SessionDep

from sqlalchemy import select



router = APIRouter(
    prefix="/notes",
    tags=["Заметки"],
)


@router.get("/", response_model=list[NoteResponse])
def read_notes(
    current_user: CurrentUser,
    session: SessionDep,
    search: str | None = None,
    limit: int | None = None,
):
    
    statement = select(Note).where(
        Note.user_id == current_user.id
    )

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
    note: CurrentNote
):
    
    return note
        

@router.get("/{note_id}/image")
def get_note_image(
    note: CurrentNote
):

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
    current_user: CurrentUser,
    session: SessionDep,
    title: str = Form(...),
    text: str = Form(...),
    image: UploadFile | None = None,
):

    image_name = None

    try:
    
        note = NoteCreate(title=title, text=text)

        if image:
            image_name = upload_image(image)

        new_note = Note(
            title=note.title,
            text=note.text,
            image=image_name,
            user_id=current_user.id
        )

        session.add(new_note)
        session.commit()
        session.refresh(new_note)

        return new_note

    except Exception:
        session.rollback()

        if image_name:
            delete_image(image_name)

        raise

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    existing_note: CurrentNote,
    session: SessionDep,
    title: str = Form(...),
    text: str = Form(...),
    image: UploadFile | None = None,
):
    
    old_image_name = None
    new_image_name = None

    try:

        note = NoteCreate(title=title, text=text)

        existing_note.title = note.title
        existing_note.text = note.text

        if existing_note.image is not None:
            old_image_name = existing_note.image

        if image:
            new_image_name = upload_image(image)
            existing_note.image = new_image_name
        else:
            existing_note.image = None
                
        session.commit()

    except Exception:
        session.rollback()

        if new_image_name:
            delete_image(new_image_name)
        raise

    if old_image_name:
        delete_image(old_image_name)

    session.refresh(existing_note)
    return existing_note
    

@router.patch("/{note_id}", response_model=NoteResponse)
def patch_note(
    existing_note: CurrentNote,
    session: SessionDep,
    title: str | None = Form(default=None),
    text: str | None = Form(default=None),
    image : UploadFile | None = None,
):
    old_image_name = None
    new_image_name = None

    try:

        note = NoteUpdate(title=title, text=text)

        if title is not None:
            existing_note.title = note.title

        if text is not None:
            existing_note.text = note.text

        if image:
            if existing_note.image is not None:
                old_image_name = existing_note.image

            new_image_name = upload_image(image)
            existing_note.image = new_image_name
                
        session.commit()

    except Exception:
        session.rollback()
        if new_image_name:
            delete_image(new_image_name)
        raise

    if old_image_name:
        delete_image(old_image_name)

    session.refresh(existing_note)

    return existing_note


@router.delete("/{note_id}")
def delete_note(
    note: CurrentNote,
    session: SessionDep,
):  
    
    old_image_name = None

    try:

        old_image_name = note.image

        session.delete(note)
        session.commit()

    except Exception:
        session.rollback()
        raise

    if old_image_name:
        delete_image(old_image_name)
    
    return {"message": "Заметка удалена"}


@router.delete("/{note_id}/image")
def delete_note_image(
    note: CurrentNote,
    session: SessionDep,
):

    old_image_name = None

    try:

        if note.image is None:
            raise HTTPException(
                status_code=404,
                detail="У заметки нет изображения"
            )
                
        old_image_name = note.image
        note.image = None

        session.commit()

    except Exception:
        session.rollback()
        raise

    if old_image_name:
        delete_image(old_image_name)

    return {"message": "Изображение удалено"}
