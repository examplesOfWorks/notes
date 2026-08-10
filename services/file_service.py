import json
from fastapi import HTTPException
from pydantic import ValidationError

from schemas.note import Note

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