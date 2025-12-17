from django.urls import path
from .views import PostListCreateView, PostDetailView, UserPostsView

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list-create'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('user/<int:user_id>/', UserPostsView.as_view(), name='user-posts'),
]
