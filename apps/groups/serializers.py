from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FriendGroup
from apps.users.serializers import UserSearchSerializer

User = get_user_model()


class FriendGroupSerializer(serializers.ModelSerializer):
    owner = UserSearchSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = FriendGroup
        fields = ('id', 'name', 'owner', 'members_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')

    def get_members_count(self, obj):
        return obj.members.count()


class FriendGroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendGroup
        fields = ('id', 'name')

    def validate_name(self, value):
        user = self.context['request'].user
        if FriendGroup.objects.filter(owner=user, name=value).exists():
            raise serializers.ValidationError('You already have a group with this name')
        return value

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class FriendGroupUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendGroup
        fields = ('name',)

    def validate_name(self, value):
        user = self.context['request'].user
        instance = self.instance
        if FriendGroup.objects.filter(owner=user, name=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError('You already have a group with this name')
        return value


class GroupMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        try:
            user = User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found')
        
        request_user = self.context['request'].user
        if user.pk == request_user.pk:
            raise serializers.ValidationError('You cannot add yourself to a group')
        
        return value


class FriendGroupDetailSerializer(serializers.ModelSerializer):
    owner = UserSearchSerializer(read_only=True)
    members = UserSearchSerializer(many=True, read_only=True)

    class Meta:
        model = FriendGroup
        fields = ('id', 'name', 'owner', 'members', 'created_at', 'updated_at')
