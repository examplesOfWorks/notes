from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from dependencies import CurrentWebUser

templates = Jinja2Templates(directory="templates")

router = APIRouter()



@router.get("/", include_in_schema=False)
def main_page(
    request: Request,
    current_user: CurrentWebUser,
):
    return templates.TemplateResponse(
        request=request,
        name="main.html",
        context={"current_user": current_user}
    )