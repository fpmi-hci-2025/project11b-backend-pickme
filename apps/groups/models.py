from django.db import models
from django.conf import settings


class FriendGroup(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_groups'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='member_of_groups',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'friend_groups'
        unique_together = ('name', 'owner')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.owner.username})"
