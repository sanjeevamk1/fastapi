from fastapi import APIRouter,Depends,Path,HTTPException
from pydantic import BaseModel, Field
from models import Todos
from database import sessionlocal
from typing import Annotated
from sqlalchemy.orm import session
from starlette import status
from .auth import verify_user

router = APIRouter(
    prefix="/admin",
    tags=['admin']
)

def get_db():
    db =  sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependecy = Annotated[session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(verify_user)]

@router.get('/todo',status_code=status.HTTP_200_OK)
async def get_data(user:user_dependency,db:db_dependecy):
    if user is None:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorixed")
    if user.get('role') == 'Admin':
        return db.query(Todos).all()
    else:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not an Admin user")