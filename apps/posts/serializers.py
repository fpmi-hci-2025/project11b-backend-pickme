from rest_framework import serializers
from .models import Post, Like
from apps.users.serializers import UserSearchSerializer
from apps.groups.models import FriendGroup


class PostCreateSerializer(serializers.ModelSerializer):
    audience_groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=FriendGroup.objects.all(),
        required=False
    )

    class Meta:
        model = Post
        fields = (
            'id', 'content_type', 'text_content', 'media_file',
            'media_url', 'media_type', 'audience_type', 'audience_groups'
        )

    def validate_audience_groups(self, value):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication required')
        user_groups = FriendGroup.objects.filter(owner=request.user)
        for group in value:
            if group not in user_groups:
                raise serializers.ValidationError(
                    f'Group "{group.name}" does not belong to you'
                )
        return value

    def validate(self, attrs):
        content_type = attrs.get('content_type')
        text_content = attrs.get('text_content')
        media_file = attrs.get('media_file')
        media_url = attrs.get('media_url')
        media_type = attrs.get('media_type')
        audience_type = attrs.get('audience_type')
        audience_groups = attrs.get('audience_groups', [])

        if content_type == Post.ContentType.TEXT:
            if not text_content:
                raise serializers.ValidationError({
                    'text_content': 'Text content is required for text posts'
                })
            attrs['media_file'] = None
            attrs['media_url'] = ''
            attrs['media_type'] = ''

        elif content_type == Post.ContentType.MEDIA:
            if not media_file and not media_url:
                raise serializers.ValidationError({
                    'media_file': 'Media file or URL is required for media posts'
                })
            if not media_type:
                raise serializers.ValidationError({
                    'media_type': 'Media type is required for media posts'
                })
            if media_type == Post.MediaType.LINK and not media_url:
                raise serializers.ValidationError({
                    'media_url': 'URL is required for link type'
                })
            attrs['text_content'] = attrs.get('text_content', '')

        if audience_type == Post.AudienceType.GROUPS and not audience_groups:
            raise serializers.ValidationError({
                'audience_groups': 'At least one group is required when audience type is "groups"'
            })

        return attrs

    def create(self, validated_data):
        audience_groups = validated_data.pop('audience_groups', [])
        validated_data['author'] = self.context['request'].user
        post = Post.objects.create(**validated_data)
        
        if audience_groups:
            post.audience_groups.set(audience_groups)
        
        return post


class PostUpdateSerializer(serializers.ModelSerializer):
    audience_groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=FriendGroup.objects.all(),
        required=False
    )

    class Meta:
        model = Post
        fields = ('text_content', 'audience_type', 'audience_groups')

    def validate_audience_groups(self, value):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication required')
        user_groups = FriendGroup.objects.filter(owner=request.user)
        for group in value:
            if group not in user_groups:
                raise serializers.ValidationError(
                    f'Group "{group.name}" does not belong to you'
                )
        return value

    def validate(self, attrs):
        instance = self.instance
        audience_type = attrs.get('audience_type', instance.audience_type)
        audience_groups = attrs.get('audience_groups')

        if audience_type == Post.AudienceType.GROUPS:
            if audience_groups is not None and not audience_groups:
                raise serializers.ValidationError({
                    'audience_groups': 'At least one group is required'
                })

        return attrs

    def update(self, instance, validated_data):
        audience_groups = validated_data.pop('audience_groups', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if audience_groups is not None:
            instance.audience_groups.set(audience_groups)
        
        return instance


class LikeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'created_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSearchSerializer(instance.user).data
        return data


class PostSerializer(serializers.ModelSerializer):
    author = UserSearchSerializer(read_only=True)
    audience_groups_detail = serializers.SerializerMethodField()
    is_own = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    liked_by = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'author', 'content_type', 'text_content', 'media_file',
            'media_url', 'media_type', 'audience_type', 'audience_groups',
            'audience_groups_detail', 'is_own', 'likes_count', 'is_liked',
            'liked_by', 'created_at', 'updated_at'
        )

    def get_audience_groups_detail(self, obj):
        return [{'id': g.id, 'name': g.name} for g in obj.audience_groups.all()]

    def get_is_own(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_liked_by(self, obj):
        likes = obj.likes.select_related('user').order_by('-created_at')
        return [UserSearchSerializer(like.user).data for like in likes]
