from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import FriendGroup
from .serializers import (
    FriendGroupSerializer,
    FriendGroupCreateSerializer,
    FriendGroupUpdateSerializer,
    FriendGroupDetailSerializer,
    GroupMemberSerializer,
)
from apps.users.serializers import UserSearchSerializer

User = get_user_model()


class IsGroupOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class FriendGroupListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return FriendGroup.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FriendGroupCreateSerializer
        return FriendGroupSerializer


class FriendGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, IsGroupOwner)

    def get_queryset(self):
        return FriendGroup.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return FriendGroupUpdateSerializer
        return FriendGroupDetailSerializer


class GroupMembersListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated, IsGroupOwner)
    serializer_class = UserSearchSerializer

    def get_queryset(self):
        group = get_object_or_404(
            FriendGroup,
            pk=self.kwargs['group_id'],
            owner=self.request.user
        )
        return group.members.all()


class GroupMemberAddView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, group_id):
        group = get_object_or_404(FriendGroup, pk=group_id, owner=request.user)
        
        serializer = GroupMemberSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        user = User.objects.get(pk=user_id)
        
        if group.members.filter(pk=user_id).exists():
            return Response(
                {'detail': 'User is already in this group'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        group.members.add(user)
        return Response(
            {'detail': 'User added to group'},
            status=status.HTTP_201_CREATED
        )


class GroupMemberRemoveView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, group_id, user_id):
        group = get_object_or_404(FriendGroup, pk=group_id, owner=request.user)
        user = get_object_or_404(User, pk=user_id)
        
        if not group.members.filter(pk=user_id).exists():
            return Response(
                {'detail': 'User is not in this group'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        group.members.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
