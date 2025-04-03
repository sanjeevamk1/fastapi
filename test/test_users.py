from http.client import responses

from .utils import *
from ..router.auth import get_db,verify_user,authenticate_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[verify_user] = override_get_user

def test_get_user(test_user):
    response = client.get('/auth/getusers')
    assert response.status_code == status.HTTP_200_OK

def test_change_password(test_user):
    response = client.put('/auth/change_password',json={"old_password":"test@123","new_password":"testad@123"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_fail(test_user):
    response = client.put('/auth/change_password',json={"old_password":"jaia@123","new_password":"aac@123"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':"Old Password Incorrect"}
