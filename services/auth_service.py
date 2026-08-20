from fastapi import Depends, HTTPException, Cookie
import jwt
from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from database import get_session
from models import User


SECRET_KEY = "some-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api-users/login"
)

def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_api_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Некорректный токен"
            )
        
        user_id = int(user_id)

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Некорректный токен"
        )

    user = session.get(User, int(user_id))

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    return user


def get_current_web_user(
    access_token: str | None = Cookie(default=None),
    session: Session = Depends(get_session)
):
    if access_token is None:
        return None
    
    try:
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            return None

    except jwt.InvalidTokenError:
        return None

    user = session.get(User, int(user_id))

    if user is None:
        return None

    return user

