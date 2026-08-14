from fastapi import FastAPI
import uvicorn
from routers.notes import router as notes_router
from routers.users import router as users_router

from database import engine
from models import Base


app = FastAPI()


app.include_router(notes_router)
app.include_router(users_router)


Base.metadata.create_all(engine)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

