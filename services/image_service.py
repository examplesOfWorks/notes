from fastapi import HTTPException, UploadFile
from pathlib import Path
from uuid import uuid4


PATH_TO_IMAGES = Path("images")
PATH_TO_IMAGES.mkdir(exist_ok=True)

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

    path = PATH_TO_IMAGES / file.filename

    with open(path, "wb") as buffer:
        buffer.write(file.file.read())

    return file.filename

def delete_image(filename: str):
    path = PATH_TO_IMAGES / filename

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Файл изображения не найден"
        )
    
    if path.exists():
        path.unlink()