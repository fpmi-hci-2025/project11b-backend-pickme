from django.urls import path
from ..views import (
    UserDetailView,
    UserUpdateView,
    AvatarUploadView,
    CurrentUserView,
    UserSearchView,
)

urlpatterns = [
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('<int:pk>/avatar/', AvatarUploadView.as_view(), name='avatar-upload'),
]
