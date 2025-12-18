from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q, Count

from .models import Post, Like
from .serializers import PostSerializer, PostCreateSerializer, PostUpdateSerializer
from apps.users.serializers import UserSearchSerializer

User = get_user_model()


class IsPostAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class PostListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer

    def get_queryset(self):
        user = self.request.user
        
        # Get all groups where user is a member
        user_groups = user.member_of_groups.all()
        
        # Posts visible to user:
        # 1. Own posts
        # 2. Posts with audience_type='everyone'
        # 3. Posts with audience_type='groups' where user is in one of the groups
        queryset = Post.objects.filter(
            Q(author=user) |  # Own posts
            Q(audience_type=Post.AudienceType.EVERYONE) |  # Public posts
            Q(
                audience_type=Post.AudienceType.GROUPS,
                audience_groups__in=user_groups
            )  # Posts shared with user's groups
        ).distinct().select_related('author').prefetch_related('audience_groups')
        
        return queryset


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return PostUpdateSerializer
        return PostSerializer

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        
        # Check view permission
        if not obj.can_view(user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to view this post")
        
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'You can only edit your own posts'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'You can only delete your own posts'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class UserPostsView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PostSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        current_user = self.request.user
        
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Post.objects.none()
        
        # If viewing own posts, show all
        if target_user == current_user:
            return Post.objects.filter(author=target_user)
        
        # Get groups where current_user is a member (owned by target_user)
        user_groups = current_user.member_of_groups.filter(owner=target_user)
        
        # Show:
        # 1. Public posts
        # 2. Posts shared with groups that current_user is a member of
        queryset = Post.objects.filter(
            Q(author=target_user) & (
                Q(audience_type=Post.AudienceType.EVERYONE) |
                Q(
                    audience_type=Post.AudienceType.GROUPS,
                    audience_groups__in=user_groups
                )
            )
        ).distinct()

        return queryset


class PostLikeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_post(self, pk):
        try:
            post = Post.objects.get(pk=pk)
            if not post.can_view(self.request.user):
                return None
            return post
        except Post.DoesNotExist:
            return None

    def get_liked_by(self, post):
        likes = post.likes.select_related('user').order_by('-created_at')
        return [UserSearchSerializer(like.user).data for like in likes]

    def post(self, request, pk):
        """Like a post"""
        post = self.get_post(pk)
        if not post:
            return Response(
                {'detail': 'Post not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )

        like, created = Like.objects.get_or_create(user=request.user, post=post)
        return Response({
            'detail': 'Post liked' if created else 'Post already liked',
            'likes_count': post.likes.count(),
            'liked_by': self.get_liked_by(post),
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, pk):
        """Unlike a post"""
        post = self.get_post(pk)
        if not post:
            return Response(
                {'detail': 'Post not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )

        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        return Response({
            'detail': 'Like removed' if deleted else 'Post was not liked',
            'likes_count': post.likes.count(),
            'liked_by': self.get_liked_by(post),
        }, status=status.HTTP_200_OK)
