from .utils import *
from fastapi import  status
from ..router.admin import get_db,verify_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[verify_user] = override_get_user

def test_get_all(test_todos):
    response = client.get('/admin/todo')
    assert response.status_code == status.HTTP_200_OK
