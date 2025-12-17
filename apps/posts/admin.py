from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content_type', 'audience_type', 'created_at')
    list_filter = ('content_type', 'audience_type', 'media_type', 'created_at')
    search_fields = ('author__email', 'author__username', 'text_content')
    raw_id_fields = ('author',)
    filter_horizontal = ('audience_groups',)
    readonly_fields = ('created_at', 'updated_at')
