from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse


from schemas.note import Note, NoteCreate, NoteUpdate
from services.file_service import read_file, write_file
from services.image_service import upload_image, delete_image, PATH_TO_IMAGES


router = APIRouter(
    prefix="/notes",
    tags=["Заметки"],
)

PATH_TO_FILE = "notes.json"


@router.get("/", response_model=list[Note])
def read_notes(search: str | None = None, limit: int | None = None):
    notes = read_file(PATH_TO_FILE)
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
    notes = read_file(PATH_TO_FILE)

    for note in notes:
        if note.id == note_id:
            return note
        
    raise HTTPException(status_code=404, detail="Заметка не найдена")

@router.get("/{note_id}/image")
def get_note_image(note_id: int):
    notes = read_file(PATH_TO_FILE)

    for note in notes:
        if note.id == note_id:

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
        
    raise HTTPException(status_code=404, detail="Заметка не найдена")
        
@router.post("/", response_model=Note)
def create_note(
    title: str = Form(...),
    text: str = Form(...),
    image: UploadFile | None = None
):

    note = NoteCreate(title=title, text=text)

    notes = read_file(PATH_TO_FILE)

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
    write_file(PATH_TO_FILE, notes)

    return new_note

@router.put("/{note_id}", response_model=Note)
def update_note(note_id: int,
    title: str = Form(...),
    text: str = Form(...),
    image: UploadFile | None = None
):

    note = NoteCreate(title=title, text=text)

    notes = read_file(PATH_TO_FILE)

    image_name = None

    for existing_note in notes:
        if existing_note.id == note_id:
            existing_note.title = note.title
            existing_note.text = note.text

            if existing_note.image is not None:
                delete_image(existing_note.image)
                existing_note.image = None

            if image:
                image_name = upload_image(image)
                existing_note.image = image_name
            
            write_file(PATH_TO_FILE, notes)
            return existing_note

    raise HTTPException(status_code=404, detail="Заметка не найдена")

@router.patch("/{note_id}", response_model=Note)
def patch_note(note_id: int, 
    title: str | None = Form(default=None),
    text: str | None = Form(default=None),
    image : UploadFile | None = None
):
    
    note = NoteUpdate(title=title, text=text)

    notes = read_file(PATH_TO_FILE)

    image_name = None

    for existing_note in notes:
        if existing_note.id == note_id:

            if title is not None:
                existing_note.title = note.title

            if text is not None:
                existing_note.text = note.text

            if image:
                if existing_note.image is not None:
                    delete_image(existing_note.image)

                image_name = upload_image(image)
                existing_note.image = image_name
            
            write_file(PATH_TO_FILE, notes)
            return existing_note

    raise HTTPException(status_code=404, detail="Заметка не найдена")

@router.delete("/{note_id}")
def delete_note(note_id: int):
    notes = read_file(PATH_TO_FILE)

    for note in notes:
        if note.id == note_id:

            if note.image is not None:
                delete_image(note.image)

            notes.remove(note)
            write_file(PATH_TO_FILE, notes)

            return {"message": "Заметка удалена"}
        
    raise HTTPException(status_code=404, detail="Заметка не найдена")

@router.delete("/{note_id}/image")
def delete_note_image(note_id: int):
    notes = read_file(PATH_TO_FILE)

    for note in notes:
        if note.id == note_id:

            if note.image is None:
                raise HTTPException(
                    status_code=404,
                    detail="У заметки нет изображения"
                )
            
            delete_image(note.image)
            note.image = None

            write_file(PATH_TO_FILE, notes)

            return {"message": "Изображение удалено"}
        
    raise HTTPException(status_code=404, detail="Заметка не найдена")

