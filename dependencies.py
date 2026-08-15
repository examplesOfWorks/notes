from typing import Annotated

from fastapi import Depends

from models import Note, User
from services.auth_service import get_current_user
from services.note_service import get_current_note

from sqlalchemy.orm import Session
from database import get_session


CurrentUser = Annotated[
    User,
    Depends(get_current_user)
]

CurrentNote = Annotated[
    Note,
    Depends(get_current_note)
]

SessionDep = Annotated[
    Session,
    Depends(get_session)
]