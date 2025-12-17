import pytest
from django.urls import reverse
from rest_framework import status
from apps.posts.models import Post


@pytest.mark.django_db
class TestPosts:
    def test_create_text_post(self, authenticated_client, user):
        url = reverse('post-list-create')
        data = {
            'content_type': 'text',
            'text_content': 'Hello world!',
            'audience_type': 'everyone'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(author=user).exists()

    def test_create_post_groups_audience(self, authenticated_client, friend_group):
        url = reverse('post-list-create')
        data = {
            'content_type': 'text',
            'text_content': 'Private post',
            'audience_type': 'groups',
            'audience_groups': [friend_group.pk]
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_list_posts(self, authenticated_client, post):
        url = reverse('post-list-create')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_private_post_visibility(self, api_client, user, another_user, friend_group):
        # Create private post
        private_post = Post.objects.create(
            author=user,
            content_type=Post.ContentType.TEXT,
            text_content='Private content',
            audience_type=Post.AudienceType.GROUPS
        )
        private_post.audience_groups.add(friend_group)
        
        # Another user without group membership
        api_client.force_authenticate(user=another_user)
        url = reverse('post-detail', kwargs={'pk': private_post.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_private_post_visible_to_group_member(self, api_client, user, another_user, friend_group):
        friend_group.members.add(another_user)
        
        private_post = Post.objects.create(
            author=user,
            content_type=Post.ContentType.TEXT,
            text_content='Shared content',
            audience_type=Post.AudienceType.GROUPS
        )
        private_post.audience_groups.add(friend_group)
        
        api_client.force_authenticate(user=another_user)
        url = reverse('post-detail', kwargs={'pk': private_post.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_delete_own_post(self, authenticated_client, post):
        url = reverse('post-detail', kwargs={'pk': post.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
