import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.groups.models import FriendGroup
from apps.posts.models import Post

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123'
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email='another@example.com',
        username='anotheruser',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def friend_group(db, user):
    return FriendGroup.objects.create(
        name='Test Group',
        owner=user
    )


@pytest.fixture
def post(db, user):
    return Post.objects.create(
        author=user,
        content_type=Post.ContentType.TEXT,
        text_content='Test post content',
        audience_type=Post.AudienceType.EVERYONE
    )
