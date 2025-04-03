from .utils import *
from ..router.auth import get_db, authenticate_user, generate_token, Secret_key, Algorithm, verify_user
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db



def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'admin'
    expires_delta = 20

    token = generate_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, Secret_key, algorithms=[Algorithm],
                               options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role








