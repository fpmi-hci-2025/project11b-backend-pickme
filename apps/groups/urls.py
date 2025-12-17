from django.urls import path
from .views import (
    FriendGroupListCreateView,
    FriendGroupDetailView,
    GroupMembersListView,
    GroupMemberAddView,
    GroupMemberRemoveView,
)

urlpatterns = [
    path('', FriendGroupListCreateView.as_view(), name='group-list-create'),
    path('<int:pk>/', FriendGroupDetailView.as_view(), name='group-detail'),
    path('<int:group_id>/members/', GroupMembersListView.as_view(), name='group-members-list'),
    path('<int:group_id>/members/add/', GroupMemberAddView.as_view(), name='group-member-add'),
    path('<int:group_id>/members/<int:user_id>/', GroupMemberRemoveView.as_view(), name='group-member-remove'),
]
