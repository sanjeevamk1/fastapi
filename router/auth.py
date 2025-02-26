from datetime import timedelta,datetime,timezone
from tokenize import Token
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

def authenticate_user(username: str, password: str, db: Session):
    data = db.query(Users).filter(Users.username == username).first()
    if data and hashed.verify(password, data.hashed_password):
        return data
    raise HTTPException(status_code=401, detail='Invalid username or password')


def generate_token(username: str, user_id: int, minute: int):
    payload = {'sub': username, 'id': user_id, 'exp': datetime.now(timezone.utc) + timedelta(minutes=minute)}
    return jwt.encode(payload, Secret_key, algorithm=Algorithm)

def verify_user(token:Annotated[str,Depends(bearer)]):
    try:
        data = jwt.decode(token,Secret_key,algorithms=[Algorithm])
        username = data.get('sub')
        user_id = data.get('id')
        if user_id is None or username is None:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not able to verify JWT")
        else:
            return {'username':username,'user_id':user_id}
    except JWTError:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not able to verify JWT")

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

    token = generate_token(user.username, user.id, 20)
    return {"access_token": token, "token_type": "bearer"}

@router.get('/getusers',status_code=status.HTTP_200_OK)
async def get_users(db:db_dependecy):
    return db.query(Users).all()