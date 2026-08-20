from typing import Annotated

from fastapi import Depends

from models import Note, User
from services.auth_service import get_current_api_user, get_current_web_user
from services.note_service import get_current_note, get_current_note_web

from sqlalchemy.orm import Session
from database import get_session


CurrentUser = Annotated[
    User,
    Depends(get_current_api_user)
]

CurrentWebUser = Annotated[
    User,
    Depends(get_current_web_user)
]

CurrentNote = Annotated[
    Note,
    Depends(get_current_note)
]

CurrentWebNote = Annotated[
    Note,
    Depends(get_current_note_web)
]

SessionDep = Annotated[
    Session,
    Depends(get_session)
]