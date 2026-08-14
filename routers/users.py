from fastapi import APIRouter, Depends, HTTPException

from models import User
from schemas.user import UserCreate, UserResponse, UserLogin

from security import hash_password, verify_password

from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_session

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    session: Session = Depends(get_session)
):
    
    try:

        statement = select(User).where(
            User.username == user.username
        )

        existing_user = session.scalar(statement)

        if existing_user is not None:
            raise HTTPException(
                status_code=400,
                detail="Пользователь с таким именем уже существует"
            )

        hashed_password = hash_password(user.password)

        new_user = User(
            username=user.username,
            hashed_password=hashed_password
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return new_user

    except Exception:
        session.rollback()
        raise


@router.post("/login")
def login_user(
    user: UserLogin,
    session: Session = Depends(get_session)
):
    
    statement = select(User).where(
        User.username == user.username
    )

    existing_user = session.scalar(statement)

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Неверное имя пользователя или пароль"
        )
    
    if not verify_password(
        user.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Неверное имя пользователя или пароль"
        )
    
    return {"message": "Вход выполнен"}
