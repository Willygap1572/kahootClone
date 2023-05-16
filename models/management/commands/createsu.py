# models/management/commands/createsu.py

from models.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a superuser.'

    def handle(self, *args, **options):
        if not User.objects.filter(username='alumnodb').exists():
            User.objects.create_superuser(
                username='alumnodb',
                password='alumnodb'
            )
        print('Superuser has been created.')
