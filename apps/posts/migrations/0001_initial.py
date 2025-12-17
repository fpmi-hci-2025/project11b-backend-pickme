from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import apps.posts.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_type', models.CharField(choices=[('text', 'Text'), ('media', 'Media')], default='text', max_length=10)),
                ('text_content', models.TextField(blank=True, max_length=5000)),
                ('media_file', models.FileField(blank=True, null=True, upload_to=apps.posts.models.media_upload_path)),
                ('media_url', models.URLField(blank=True, max_length=2000)),
                ('media_type', models.CharField(blank=True, choices=[('photo', 'Photo'), ('video', 'Video'), ('link', 'Link')], max_length=10)),
                ('audience_type', models.CharField(choices=[('only_me', 'Only Me'), ('groups', 'Groups'), ('everyone', 'Everyone')], default='everyone', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('audience_groups', models.ManyToManyField(blank=True, related_name='posts', to='groups.friendgroup')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'posts',
                'ordering': ['-created_at'],
            },
        ),
    ]
