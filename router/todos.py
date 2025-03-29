from fastapi import APIRouter,Depends,Path,HTTPException,status
from pydantic import BaseModel, Field
from ..models import Todos
from ..database import sessionlocal
from typing import Annotated
from starlette import status
from sqlalchemy.orm import session
from .auth import verify_user

app=APIRouter()



def get_db():
    db =  sessionlocal()
    try:
        yield db
    finally:
        db.close()

class Todorequest(BaseModel):
    title :str=Field(min_length=3)
    description:str=Field(min_length=3,max_length=100)
    priority:int
    completed:bool

    model_config = {
        "json_schema_extra":{
            "example":{
                "title":"your work",
                "description":"describe work",
                "priority":"set priority of work",
                "completed":"is it done"
            }
        }
    }



db_dependecy = Annotated[session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(verify_user)]

@app.get('/',status_code=status.HTTP_200_OK)
async def get_data(user:user_dependency,db:db_dependecy):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorixed")
    return db.query(Todos).filter(Todos.owner_id==user.get('user_id')).all()

@app.get('/todos/{todo_id}',status_code=status.HTTP_200_OK)
async def get_id(user:user_dependency,db:db_dependecy,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorixed")
    result = db.query(Todos).filter(Todos.id==todo_id).filter(Todos.owner_id == user.get('user_id')).first()
    if  result is not None:
        return result
    raise HTTPException(status_code=404,detail="Id not found")

@app.post('/todos',status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency,db:db_dependecy,req:Todorequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorixed")
    model = Todos(**req.model_dump(),owner_id=user.get('user_id'))
    db.add(model)
    db.commit()
    return {"message":"added successfully"}

@app.put('/todos/{todo_id}',status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user:user_dependency,db:db_dependecy,req:Todorequest,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorixed")
    model = Todos(**req.model_dump())
    data =  db.query(Todos).filter(Todos.id==todo_id).filter(Todos.owner_id == user.get('user_id')).first()
    if data:
        data.title=model.title
        data.description = model.description
        data.priority = model.priority
        data.completed=model.completed
        db.add(data)
        db.commit()
        return {"message":"Updated Successfully"}
    else:
        raise HTTPException(status_code=404,detail="not found")

@app.delete('/todos/{todo_id}',status_code=status.HTTP_200_OK)
async def delete_todouser(user: user_dependency,db:db_dependecy,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorixed")
    model = db.query(Todos).filter(Todos.id==todo_id).filter(Todos.owner_id == user.get('user_id')).first()
    if model:
        db.query(Todos).filter(Todos.id==todo_id).delete()
        db.commit()
        return {"message":"deleted successfully"}
    else:
        raise HTTPException(status_code=404,detail="Id not found")