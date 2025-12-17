from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings


class Command(BaseCommand):
    help = 'Create a superuser if none exists'

    def handle(self, *args, **options):
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            email = settings.SUPERUSER_EMAIL
            username = settings.SUPERUSER_USERNAME
            password = settings.SUPERUSER_PASSWORD
            
            User.objects.create_superuser(
                email=email,
                username=username,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser {email} created successfully')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Superuser already exists')
            )
