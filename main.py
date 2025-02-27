from fastapi import FastAPI
import models
from database import engine
from router import auth, todos,admin

app=FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(todos.app)
app.include_router(admin.router)