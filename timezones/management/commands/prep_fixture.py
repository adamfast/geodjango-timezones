from optparse import make_option

from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand, CommandError

from timezones.models import *


class Command(BaseCommand):
    args = ''
    help = 'Delete timezones not needed for tests from the database.'

    def handle(self, *args, **options):
        unneeded_timezones = Timezone.objects.all().exclude(tzid__in=('America/Chicago', 'America/New_York'))
        unneeded_timezones.delete()
