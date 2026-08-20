from fastapi import APIRouter, Form, HTTPException, UploadFile, Request
from fastapi.responses import FileResponse, RedirectResponse

from models import Note
from schemas.note import NoteCreate, NoteUpdate

from services.image_service import upload_image, delete_image, PATH_TO_IMAGES

from dependencies import CurrentWebNote, CurrentWebUser, SessionDep

from sqlalchemy import select

from fastapi.templating import Jinja2Templates



templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/notes",
    tags=["Заметки"],
)

@router.get("/", include_in_schema=False)
def read_notes(
    request: Request,
    current_user: CurrentWebUser,
    session: SessionDep,
    search: str | None = None,
    limit: int | None = None,
):
    if not current_user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )

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

    return templates.TemplateResponse(
            request=request,
            name="notes/list.html",
            context={
                "notes": notes,
                "current_user": current_user,
                "search": search
            }
        )


@router.get("/create", include_in_schema=False)
def create_note_page(
    current_user: CurrentWebUser,
    request: Request
):
    if not current_user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )
    return templates.TemplateResponse(
        request=request,
        name="notes/create.html",
        context={
            "current_user": current_user
        }
    )


@router.post("/create", include_in_schema=False)
def create_note(
    current_user: CurrentWebUser,
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

        return RedirectResponse(
            url="/notes",
            status_code=303
        )

    except Exception:
        session.rollback()

        if image_name:
            delete_image(image_name)

        raise


@router.get("/{note_id}", include_in_schema=False)
def read_note(
    note: CurrentWebNote,
    current_user: CurrentWebUser,
    request: Request,
):
    
    if not current_user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )
    
    if not note:
        raise HTTPException(
            status_code=404,
            detail="Запрашиваемая заметка не существует или была удалена."
        )
    
    return templates.TemplateResponse(
        request=request,
        name="notes/detail.html",
        context={
            "note": note,
            "current_user": current_user,
            
        }
    )
        

@router.get("/{note_id}/image", include_in_schema=False)
def get_note_image(
    note: CurrentWebNote
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
          

@router.get("/{note_id}/edit", include_in_schema=False)
def edit_note(
    request: Request,
    current_user: CurrentWebUser,
    note: CurrentWebNote
):
    if not current_user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="notes/edit.html",
        context={
            "note": note,
            "current_user": current_user,
        }
    )


@router.post("/{note_id}/edit", include_in_schema=False)
def edit_note_post(
    existing_note: CurrentWebNote,
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

        if image and image.filename:
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

    return RedirectResponse(
        url=f"/notes/{existing_note.id}",
        status_code=303
    )


@router.post("/{note_id}/delete", include_in_schema=False)
def delete_note(
    note: CurrentWebNote,
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
    
    return RedirectResponse(
        url="/notes/",
        status_code=303
    )


@router.post("/{note_id}/image/delete", include_in_schema=False)
def delete_note_image(
    note: CurrentWebNote,
    session: SessionDep,
):

    old_image_name = None

    try:

        if note.image:

            old_image_name = note.image
            note.image = None

            session.commit()

    except Exception:
        session.rollback()
        raise

    if old_image_name:
        delete_image(old_image_name)

    return RedirectResponse(
        url=f"/notes/{note.id}/edit",
        status_code=303
    )

