from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from models import User
from schemas.user import UserCreate, UserResponse

from security import hash_password, verify_password

from services.auth_service import create_access_token

from sqlalchemy import select

from dependencies import SessionDep


router = APIRouter(
    prefix="/api-users",
    tags=["Пользователи"],
)

@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    session: SessionDep,
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
    session: SessionDep,
    user: OAuth2PasswordRequestForm = Depends(),
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
    
    access_token = create_access_token(existing_user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
