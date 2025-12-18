from django.contrib import admin
from .models import Post, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content_type', 'audience_type', 'likes_count', 'created_at')
    list_filter = ('content_type', 'audience_type', 'media_type', 'created_at')
    search_fields = ('author__email', 'author__username', 'text_content')
    raw_id_fields = ('author',)
    filter_horizontal = ('audience_groups',)
    readonly_fields = ('created_at', 'updated_at')

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__username')
    raw_id_fields = ('user', 'post')
    readonly_fields = ('created_at',)
