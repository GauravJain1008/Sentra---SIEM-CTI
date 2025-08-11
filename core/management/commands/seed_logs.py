from django.core.management.base import BaseCommand
from core.models import LogEvent
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Insert dummy logs for testing'

    def handle(self, *args, **kwargs):
        levels = ['INFO', 'WARNING', 'ERROR']
        sources = ['syslog', 'app', 'firewall']
        hosts = ['server1', 'server2', 'server3']

        for i in range(50):
            LogEvent.objects.create(
                ts=timezone.now(),
                host=random.choice(hosts),
                source=random.choice(sources),
                level=random.choice(levels),
                message=f"Test log message {i}"
            )
        self.stdout.write(self.style.SUCCESS("Inserted 50 dummy logs"))

