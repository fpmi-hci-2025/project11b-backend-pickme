import pytest
from django.urls import reverse
from rest_framework import status
from apps.groups.models import FriendGroup


@pytest.mark.django_db
class TestFriendGroups:
    def test_create_group(self, authenticated_client, user):
        url = reverse('group-list-create')
        data = {'name': 'Family'}
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert FriendGroup.objects.filter(owner=user, name='Family').exists()

    def test_list_groups(self, authenticated_client, friend_group):
        url = reverse('group-list-create')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_add_member(self, authenticated_client, friend_group, another_user):
        url = reverse('group-member-add', kwargs={'group_id': friend_group.pk})
        data = {'user_id': another_user.pk}
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert friend_group.members.filter(pk=another_user.pk).exists()

    def test_cannot_add_self_to_group(self, authenticated_client, friend_group, user):
        url = reverse('group-member-add', kwargs={'group_id': friend_group.pk})
        data = {'user_id': user.pk}
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_member(self, authenticated_client, friend_group, another_user):
        friend_group.members.add(another_user)
        url = reverse('group-member-remove', kwargs={
            'group_id': friend_group.pk,
            'user_id': another_user.pk
        })
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not friend_group.members.filter(pk=another_user.pk).exists()
