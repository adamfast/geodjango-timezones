import datetime

from geopy.point import Point as GeoPyPoint
from pytz import timezone

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
from django.core.management import call_command
from django import forms
from django.test import TestCase

from timezones.forms import LocationTimezoneAwareDateTimeField, LocationTimezoneAwareForm
from timezones.models import *
from timezones.exceptions import UnknownPointException
from timezones.management.commands.load_timezones import NoShapeFileException
from timezones.utils import time_at, timezone_for, time_for


class TimezoneTests(TestCase):

    fixtures = ['timezones.json']

    def test_admin(self):
        admin = User.objects.create(username='testadmin', is_superuser=True, is_staff=True)
        admin.set_password('stuff')
        admin.save()

        self.assertEqual(self.client.login(username='testadmin', password='stuff'), True)

        response = self.client.get('/admin/timezones/timezone/')
        self.assertEqual(response.status_code, 200)

    def test_lawrence_ks(self):
        loc = Point((-95.235278, 38.971667))  # lawrence, ks

        the_time_non_dst = datetime.datetime(2012, 2, 19, 10) # this is not during daylight savings time, -6

        the_timezone = timezone_for(loc)
        self.assertEqual(the_timezone, timezone('America/Chicago'))

        with_zone = time_at(the_time_non_dst, loc)
        self.assertEqual(str(with_zone), '2012-02-19 10:00:00-06:00')
        self.assertEqual(str(with_zone.tzinfo), 'America/Chicago')

        the_time_dst = datetime.datetime(2012, 4, 15, 10) # this is during daylight savings time, -5

        with_zone = time_at(the_time_dst, loc)
        self.assertEqual(str(with_zone), '2012-04-15 10:00:00-05:00')
        self.assertEqual(str(with_zone.tzinfo), 'America/Chicago')

        in_ny = time_for(with_zone, Point((-73.8726111, 40.7772500)))  # KLGA
        self.assertEqual(str(in_ny), '2012-04-15 11:00:00-04:00')
        self.assertEqual(str(in_ny.tzinfo), 'America/New_York')

    def test_lawrence_ks_datetime_none(self):
        loc = Point((-95.235278, 38.971667))  # lawrence, ks

        the_time_non_dst = None

        the_timezone = timezone_for(loc)
        self.assertEqual(the_timezone, timezone('America/Chicago'))

        with_zone = time_at(the_time_non_dst, loc)
        self.assertEqual(with_zone, None)

    def test_lawrence_ks_geopy(self):
        # GEOPY IS LATITUDE, LONGITUDE
        loc = GeoPyPoint(38.971667, -95.235278)  # lawrence, ks

        the_time_non_dst = datetime.datetime(2012, 2, 19, 10) # this is not during daylight savings time, -6

        the_timezone = timezone_for(loc)
        self.assertEqual(the_timezone, timezone('America/Chicago'))

        with_zone = time_at(the_time_non_dst, loc)
        self.assertEqual(str(with_zone), '2012-02-19 10:00:00-06:00')
        self.assertEqual(str(with_zone.tzinfo), 'America/Chicago')

        the_time_dst = datetime.datetime(2012, 4, 15, 10) # this is during daylight savings time, -5

        with_zone = time_at(the_time_dst, loc)
        self.assertEqual(str(with_zone), '2012-04-15 10:00:00-05:00')
        self.assertEqual(str(with_zone.tzinfo), 'America/Chicago')

        # GEOPY IS LATITUDE, LONGITUDE
        in_ny = time_for(with_zone, GeoPyPoint(40.7772500, -73.8726111))  # KLGA
        self.assertEqual(str(in_ny), '2012-04-15 11:00:00-04:00')
        self.assertEqual(str(in_ny.tzinfo), 'America/New_York')

    def test_lawrence_ks_custom(self):
        class MySpecialPoint(object):
            def __init__(self, *args, **kwargs):
                self.latitude = kwargs['latitude']
                self.longitude = kwargs['longitude']

        loc = MySpecialPoint(longitude=-95.235278, latitude=38.971667)  # lawrence, ks

        the_time_non_dst = datetime.datetime(2012, 2, 19, 10) # this is not during daylight savings time, -6

        try:
            the_timezone = timezone_for(loc)
            self.fail("Did not return expected UnknownPointException")
        except UnknownPointException:
            pass

        try:
            in_ny = timezone_for(MySpecialPoint(longitude=-73.8726111, latitude=40.7772500))  # KLGA
            self.fail("Did not return expected UnknownPointException")
        except UnknownPointException:
            pass

    def test_out_of_area(self):
        loc = Point((-99.133333, 19.433333))  # mexico city, outside the bounds of the JSON fixture
        the_time = datetime.datetime(2012, 4, 15, 10)

        the_timezone = timezone_for(loc)
        self.assertFalse(the_timezone)

        with_zone = time_at(the_time, loc)
        self.assertEqual(str(with_zone), '2012-04-15 10:00:00')
        self.assertEqual(with_zone.tzinfo, None)

    def test_double_timezones(self):
        central = Timezone.objects.get(tzid='America/Chicago')
        eastern = Timezone.objects.get(tzid='America/New_York')

        centeastern = Timezone.objects.create(tzid='faked/CentEastern', mpoly=central.mpoly + eastern.mpoly)

        loc = Point((-95.235278, 38.971667))  # lawrence, ks
        the_time = datetime.datetime(2012, 4, 15, 10)

        the_timezone = timezone_for(loc)
        self.assertFalse(the_timezone)

        with_zone = time_at(the_time, loc)
        self.assertEqual(str(with_zone), '2012-04-15 10:00:00')
        self.assertEqual(with_zone.tzinfo, None)

    def test_rogue_timezone(self):
        point1 = Point((-99.133333, 19.433333))  # mexico city, outside the bounds of the JSON fixture
        point2 = Point((-46.633333, -23.55))  # sao paulo, brazil
        point3 = Point((-78.583333, -0.25))  # quito, ecuador
        point4 = Point((-72.333333, 18.533333))

        the_mpoly = MultiPolygon(Polygon((point1, point2, point3, point4, point1)))
        the_tz = Timezone.objects.create(tzid='faked/Fakeville', mpoly=the_mpoly)

        loc = Point((-94.433333, 18.15))  # mexico city, outside the bounds of the JSON fixture
        the_time = datetime.datetime(2012, 4, 15, 10)

        the_timezone = timezone_for(loc)
        self.assertFalse(the_timezone)

        with_zone = time_at(the_time, loc)
        # now there are two results, it gets confused and doesn't know which to pick
        # this solution probably isn't optimal but the zones shouldn't overlap.
        self.assertEqual(str(with_zone), '2012-04-15 10:00:00')
        self.assertEqual(with_zone.tzinfo, None)

    def test_no_location(self):
        loc = None
        the_time = datetime.datetime(2012, 4, 15, 10)

        the_timezone = timezone_for(loc)
        self.assertFalse(the_timezone)

        with_zone = time_at(the_time, loc)
        self.assertEqual(str(with_zone), '2012-04-15 10:00:00')
        self.assertEqual(with_zone.tzinfo, None)

    def test_management(self):
        try:
            call_command('load_timezones')
            self.fail("Did not raise expected NoShapeFileException.")
        except NoShapeFileException:
            pass


class TzForm(LocationTimezoneAwareForm):
    time = LocationTimezoneAwareDateTimeField()


class TimezoneFormTests(TestCase):
    fixtures = ['timezones.json']

    loc = Point((-95.235278, 38.971667))  # lawrence, ks

    def test_no_location(self):
        form = TzForm({'time': '2013-03-18 12:00'})

        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['time'], timezone(settings.TIME_ZONE).localize(datetime.datetime(2013, 3, 18, 12)))

    def test_with_location(self):
        form = TzForm({'time': '2013-03-18 12:00'})
        form.location = self.loc

        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['time'], timezone('America/Chicago').localize(datetime.datetime(2013, 3, 18, 12)))

    def test_no_submitted(self):
        form = TzForm({})
        form.location = self.loc

        self.assertEqual(form.is_valid(), False)
