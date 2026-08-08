from fastapi import FastAPI
import uvicorn
from routers.notes import router as notes_router

app = FastAPI()


app.include_router(notes_router)




if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)