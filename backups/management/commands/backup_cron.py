from django.core.management.base import BaseCommand

from backups.tasks import run_active_backups


class Command(BaseCommand):
    args = ''
    help = 'Run all actives backups'

    def handle(self, *args, **options):
        run_active_backups.delay(args[0])
