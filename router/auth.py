from datetime import timedelta,datetime,timezone
from enum import verify
from typing import Annotated
from jose import jwt,JWTError
from fastapi import APIRouter, Depends,HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import  status
from database import sessionlocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer


Secret_key='b0057a5aae931b5facb262e780180fc3f7bdc3c8d7b04ab7a52aa7562b2fe89a'
Algorithm='HS256'
router = APIRouter(
    prefix="/auth",
    tags=['auth']
)
hashed = CryptContext(schemes=['bcrypt'],deprecated="auto")
bearer =  OAuth2PasswordBearer(tokenUrl='/auth/token')

class Requestcreateuser(BaseModel):
    username : str
    email : str
    first_name : str
    last_name : str
    role : str
    password : str

class Todo(BaseModel):
    access_token : str
    token_type :str

def get_db():
    db =  sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependecy = Annotated[Session,Depends(get_db)]

class changepasswordreq(BaseModel):
    old_password : str
    new_password : str

def authenticate_user(username: str, password: str, db: Session):
    data = db.query(Users).filter(Users.username == username).first()
    if data and hashed.verify(password, data.hashed_password):
        return data
    raise HTTPException(status_code=401, detail='Invalid username or password')


def generate_token(username: str, user_id: int, role:str,minute: int):
    payload = {'sub': username, 'id': user_id,'role':role, 'exp': datetime.now(timezone.utc) + timedelta(minutes=minute)}
    return jwt.encode(payload, Secret_key, algorithm=Algorithm)

def verify_user(token:Annotated[str,Depends(bearer)]):
    try:
        data = jwt.decode(token,Secret_key,algorithms=[Algorithm])
        username = data.get('sub')
        user_id = data.get('id')
        role =  data.get('role')
        if user_id is None or username is None:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not able to verify JWT")
        else:
            return {'username':username,'user_id':user_id,'role':role}
    except JWTError:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not able to verify JWT")

user_dependency = Annotated[dict,Depends(verify_user)]

@router.post('/auth',status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependecy,create_user_req : Requestcreateuser):
    create_user_model = Users(
        username = create_user_req.username,
        email = create_user_req.email,
        first_name = create_user_req.first_name,
        last_name = create_user_req.last_name,
        role = create_user_req.role,
        hashed_password = hashed.hash(create_user_req.password),
        is_active=True
    )
    db.add(create_user_model)
    db.commit()

    return  {"Message":"User created successfully"}


@router.post('/token', status_code=status.HTTP_200_OK)
async def authenticate(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependecy
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = generate_token(user.username, user.id, user.role,20)
    return {"access_token": token, "token_type": "bearer"}

@router.get('/getusers',status_code=status.HTTP_200_OK)
async def get_users(db:db_dependecy):
    return db.query(Users).all()

@router.get('/my_details',status_code=status.HTTP_200_OK)
async  def get_user(user:user_dependency,db:db_dependecy):
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorixed")
        return db.query(Users).filter(Users.id == user.get('user_id')).first()

@router.put('/change_password',status_code=status.HTTP_204_NO_CONTENT)
async def update_password(user:user_dependency,db:db_dependecy,req:changepasswordreq):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorixed")
    data = db.query(Users).filter(Users.id==user.get('user_id')).first()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not hashed.verify(req.old_password,data.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Old Password Incorrect")
    if hashed.verify(req.new_password,data.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Use different Password Not the old one")
    data.hashed_password = hashed.hash(req.new_password)
    db.commit()
    return {'Message':'Updated Successfully'}