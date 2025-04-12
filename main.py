from urllib.request import Request

from fastapi import FastAPI,Request,status
from .database import engine,Base
from .router import auth, todos,admin
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
app=FastAPI()

Base.metadata.create_all(bind=engine)
template  = Jinja2Templates(directory="todo_app/templates")

app.mount('/staic',StaticFiles(directory="todo_app/static"),name="static")

@app.get('/health')
async def helath_status():
    return {'status':'Healthy'}

@app.get('/')
async def start_page():
    return RedirectResponse(url='/todos/todo-page',status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(todos.app)
app.include_router(admin.router)
