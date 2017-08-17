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


def timezone_boundary_builder_import(path=''):
    from django.contrib.gis.gdal import DataSource

    timezone_mapping = {
        'tzid': 'tzid',
        'mpoly': 'POLYGON',
    }
    if os.path.exists(path):
        # spelunk the source
        ds = DataSource(path)
        layer = ds[0]
        print('Fields: %s' % layer.fields)
        print('Geom Type: %s' % layer.geom_type)
        print('SRS: %s' % layer.srs)

        lm = LayerMapping(Timezone, path, timezone_mapping)
        lm.save(verbose=True)
    else:
        raise NoShapeFileException


class Command(BaseCommand):
    args = ''
    help = 'Load timezones from the shapefile into the database.'

    def add_arguments(self, parser):
        parser.add_argument('--path', default='', dest='path',
                            help='The directory where the timezone shapefile is stored.')
        parser.add_argument('--tz_world', default=False, dest='tz_world', help='Use old tz_world dataset')
        parser.add_argument('--clear_timezones', default=False, dest='clear_timezones', action='store_true',
                            help='Clear all timezones before import')

    def handle(self, *args, **options):
        base_path = options['path']

        if options['clear_timezones']:
            print("Clearing all timezones...")
            Timezone.objects.all().delete()
            print('Done clearing all timezones.')

        if options['tz_world']:  # legacy mode
            # for backwards compatibility, the PATH argument here is a folder, not a file.
            timezone_import(base_path)

        else:  # geometries from https://github.com/evansiroky/timezone-boundary-builder
            # because it makes more sense now, this PATH is to the complete shapefile
            timezone_boundary_builder_import(base_path)
