# notifications/tests/conftest.py

import pytest

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@pytest.fixture
def user(db):

    return User.objects.create_user(
        email="user@test.com",
        password="123456",
        full_name="Test User",
    )


@pytest.fixture
def second_user(db):

    return User.objects.create_user(
        email="second@test.com",
        password="123456",
        full_name="Second User",
    )


@pytest.fixture
def access_token(user):

    token = AccessToken.for_user(user)

    return str(token)