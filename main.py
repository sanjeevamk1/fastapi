from fastapi import FastAPI
from .database import engine,Base
from .router import auth, todos,admin

app=FastAPI()

@app.get('/health')
async def helath_status():
    return {'status':'Healthy'}

Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(todos.app)
app.include_router(admin.router)