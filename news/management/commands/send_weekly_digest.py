from django.core.management.base import BaseCommand
from news.tasks import send_weekly_digest


class Command(BaseCommand):
    help = 'Send weekly digest to subscribers'

    def handle(self, *args, **options):
        send_weekly_digest.delay()
        self.stdout.write(self.style.SUCCESS('Weekly digest sent successfully'))