from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from models import User
from schemas.user import UserCreate

from security import hash_password, verify_password

from services.auth_service import create_access_token

from sqlalchemy import select

from dependencies import SessionDep

from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

@router.get("/register", include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="users/register.html"
    )

@router.post("/register", include_in_schema=False)
def register_user(
    request: Request,
    session: SessionDep,
    username: str = Form(...),
    password: str = Form(...)
):
    
    try:
        user = UserCreate(
            username=username,
            password=password
        )

        statement = select(User).where(
            User.username == user.username
        )

        existing_user = session.scalar(statement)

        if existing_user is not None:
            return templates.TemplateResponse(
                request=request,
                name="users/register.html",
                context={
                    "error": "Пользователь с таким именем уже существует",
                    "user": username
                },
                status_code=400
            )

        hashed_password = hash_password(user.password)

        new_user = User(
            username=user.username,
            hashed_password=hashed_password
        )
        
        session.add(new_user)
        session.commit()

        return RedirectResponse(
            url="/users/login",
            status_code=302
        )

    except Exception:
        session.rollback()
        raise


@router.get("/login", include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="users/login.html"
    )


@router.post("/login", include_in_schema=False)
def login_user(
    session: SessionDep,
    username: str = Form(...),
    password: str = Form(...),
):
    
    statement = select(User).where(
        User.username == username
    )

    existing_user = session.scalar(statement)

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Неверное имя пользователя или пароль"
        )
    
    if not verify_password(
        password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Неверное имя пользователя или пароль"
        )
    
    access_token = create_access_token(existing_user.id)

    response = RedirectResponse(
        url="/notes",
        status_code=303
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True
    )

    return response


@router.get("/logout", include_in_schema=False)
def logout_user():
    response = RedirectResponse(
        url="/users/login",
        status_code=303
    )

    response.delete_cookie("access_token")

    return response