from .utils import *
from ..router.auth import get_db,verify_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[verify_user] = override_get_user

def test_get_user(test_user):
    response = client.get('/auth/getusers')
    assert response.status_code == status.HTTP_200_OK