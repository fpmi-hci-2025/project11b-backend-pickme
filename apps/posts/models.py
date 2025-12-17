from django.db import models
from django.conf import settings
import uuid


def media_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'posts/{instance.author.id}/{uuid.uuid4()}.{ext}'


class Post(models.Model):
    class ContentType(models.TextChoices):
        TEXT = 'text', 'Text'
        MEDIA = 'media', 'Media'

    class MediaType(models.TextChoices):
        PHOTO = 'photo', 'Photo'
        VIDEO = 'video', 'Video'
        LINK = 'link', 'Link'

    class AudienceType(models.TextChoices):
        ONLY_ME = 'only_me', 'Only Me'
        GROUPS = 'groups', 'Groups'
        EVERYONE = 'everyone', 'Everyone'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content_type = models.CharField(
        max_length=10,
        choices=ContentType.choices,
        default=ContentType.TEXT
    )
    text_content = models.TextField(max_length=5000, blank=True)
    media_file = models.FileField(upload_to=media_upload_path, null=True, blank=True)
    media_url = models.URLField(max_length=2000, blank=True)
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        blank=True
    )
    audience_type = models.CharField(
        max_length=20,
        choices=AudienceType.choices,
        default=AudienceType.EVERYONE
    )
    audience_groups = models.ManyToManyField(
        'groups.FriendGroup',
        related_name='posts',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"

    def can_view(self, user):
        """Check if user can view this post"""
        if self.author == user:
            return True
        
        if self.audience_type == self.AudienceType.ONLY_ME:
            return False
        
        if self.audience_type == self.AudienceType.EVERYONE:
            return True
        
        if self.audience_type == self.AudienceType.GROUPS:
            # Check if user is in any of the audience groups
            return self.audience_groups.filter(members=user).exists()
        
        return False
