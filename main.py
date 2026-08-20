from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

from routers.web_main_page import router as main_page_router

from routers.api_notes import router as api_notes_router
from routers.api_users import router as api_users_router

from routers.web_notes import router as web_notes_router
from routers.web_users import router as web_users_router

from database import engine
from models import Base

from sqlalchemy.orm import Session
from services.auth_service import get_current_web_user


templates = Jinja2Templates(directory="templates")


app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

app.include_router(main_page_router)

app.include_router(api_notes_router)
app.include_router(api_users_router)

app.include_router(web_notes_router)
app.include_router(web_users_router)


Base.metadata.create_all(engine)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    with Session(engine) as session:
        current_user = get_current_web_user(
            access_token=request.cookies.get("access_token"),
            session=session,
        )

    if request.url.path.startswith("/notes/"):
        return templates.TemplateResponse(
            request=request,
            name="errors/404.html",
            status_code=404,
            context={
                "request": request,
                "detail": "",
                "current_user": current_user
            },
        )

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(404)
def not_found_page(request: Request, exc):
    if "api" in request.url.path:
        return JSONResponse(
            status_code=404,
            content={"detail": exc.detail}
        )
    
    with Session(engine) as session:
        current_user = get_current_web_user(
            access_token=request.cookies.get("access_token"),
            session=session,
        )
    
    return templates.TemplateResponse(
        request=request,
        name="errors/404.html",
        status_code=404,
        context={
            "request": request,
            "detail": exc.detail if exc.detail != "Not Found" else "",
            "current_user": current_user
        }
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

