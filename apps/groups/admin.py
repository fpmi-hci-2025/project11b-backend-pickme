from django.contrib import admin
from .models import FriendGroup


@admin.register(FriendGroup)
class FriendGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'members_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'owner__email', 'owner__username')
    raw_id_fields = ('owner',)
    filter_horizontal = ('members',)

    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = 'Members'
