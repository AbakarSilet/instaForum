import json
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Dump data with UTF-8 encoding'

    def handle(self, *args, **kwargs):
        apps_to_dump = ['news', 'events', 'modelUser', 'messaging','resources']
        with open('data_backup.json', 'w', encoding='utf-8') as f:
            call_command('dumpdata', *apps_to_dump, indent=4, stdout=f)
        self.stdout.write(self.style.SUCCESS('Data dumped successfully with UTF-8 encoding'))
