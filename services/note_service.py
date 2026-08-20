from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models import Note, User
from services.auth_service import get_current_api_user, get_current_web_user


def get_current_note(
    note_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_api_user)
):
    statement = select(Note).where(
        Note.id == note_id,
        Note.user_id == current_user.id
    )

    note = session.scalar(statement)

    if note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    
    return note
        

def get_current_note_web(
    note_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_web_user)
):
    if current_user:
        statement = select(Note).where(
            Note.id == note_id,
            Note.user_id == current_user.id
        )

        note = session.scalar(statement)
    
        return note