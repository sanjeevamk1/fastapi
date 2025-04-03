
from .utils import *
from ..router.todos import get_db
from ..router.auth import verify_user
from starlette import status
from ..models import Todos


app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[verify_user]=override_get_user

def test_get_all(test_todos):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{ 'title':'test the code',
    'description' : 'Pytest working',
    'priority' : 3,
    'completed' : True,
    'owner_id' :1,
    'id':1}]

def test_get_one(test_todos):
    response = client.get('/todos/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == { 'title':'test the code',
    'description' : 'Pytest working',
    'priority' : 3,
    'completed' : True,
    'owner_id' :1,
    'id':1}

def test_get_not_found():
    response = client.get('/todos/999')
    print(response,response.json())
    assert response.status_code == 404
    assert response.json() == {'detail': 'Id not found'}

def test_create_todo(test_todos):
    request_body = {
        "title":"tester",
        "description" :"test create",
        "priority":3,
        "completed":False,
        "owner_id":1
    }

    response = client.post('/todos',json = request_body)
    assert response.status_code == 201

    db = Test_session()
    test_data = db.query(Todos).filter(Todos.id ==2).first()
    assert test_data.title == request_body.get('title')


def test_update_todo(test_todos):
    request_body = {
        "title":"updated tester",
        "description" :"test create",
        "priority":3,
        "completed":False,
        "owner_id": 1
    }

    response = client.put('/todos/1',json = request_body)
    assert response.status_code == 204

    db = Test_session()
    test_data = db.query(Todos).filter(Todos.id ==1).first()
    assert test_data.title == request_body.get('title')

def test_update_todo_not_found():
    request_body = {
        "title":"updated tester",
        "description" :"test create",
        "priority":3,
        "completed":False
    }

    response = client.put('/todos/999',json = request_body)
    assert response.status_code == 404

def test_delete_todo(test_todos):
    response = client.delete('/todos/1')
    assert response.status_code == 200
    assert response.json() == {"message":"deleted successfully"}
    db = Test_session()
    result = db.query(Todos).filter(Todos.id == 1).first()
    assert result is None

def test_delete_todo_not_found():
    response = client.delete('/todos/899')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Id not found'}