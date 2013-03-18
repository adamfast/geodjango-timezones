import os

from optparse import make_option

from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand, CommandError

from timezones.models import *


class NoShapeFileException(Exception):
    pass


def timezone_import(path=''):  # pragma: no cover
    timezone_mapping = {
        'tzid': 'TZID',
        'mpoly': 'POLYGON',
    }
    timezone_shp = os.path.join(path, "tz_world_mp.shp")
    if os.path.exists(timezone_shp):
        lm = LayerMapping(Timezone, timezone_shp, timezone_mapping)
        lm.save(verbose=True)
    else:
        raise NoShapeFileException


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--path', default='', dest='path',
            help='The directory where the timezone shapefile is stored.'),
    )

    args = ''
    help = 'Load timezones from the shapefile into the database.'

    def handle(self, *args, **options):
        base_path = options['path']

        timezone_import(base_path)
