import logging

# geopy is not required, but if users want to specify one of their points, work with it
try:
    from geopy.point import Point
except ImportError:
    pass

from django.contrib.gis.geos import Point
from pytz import timezone, UnknownTimeZoneError

from timezones.exceptions import UnknownPointException
from timezones.models import *


logger = logging.getLogger(__name__)


def timezone_for(location):
    """Determine what timezone the provided location falls in."""

    if location is not None:
        try:
            location.wkt
        except AttributeError:  # it's not a GeoDjango point. Is it GeoPy?
            try:
                location.POINT_PATTERN  # try something a GeoPy Point would have
                location = Point(location.longitude, location.latitude, location.altitude)
            except AttributeError:
                # in the interest of not going on forever here, I'm going to punt on supporting custom classes even with obvious names (lat/lon); though I'm not opposed to doing that
                raise UnknownPointException

        the_timezones = Timezone.objects.filter(mpoly__contains=location)
        tzinfo = False

        if the_timezones.count() == 1:  # one timezone - this is normal
            the_timezone = the_timezones[0]
        elif the_timezones.count() == 0:  # no timezone found for that location
            the_timezone = False
        else:  # multiple returned - is there anywhere that will trigger that?
            # how do we determine?
            the_timezone = False

        try:
            if the_timezone != False:
                tzinfo = timezone(the_timezone.tzid)
        except UnknownTimeZoneError:
            pass

        return tzinfo

    return False


def time_at(the_datetime, location):
    """
    Determine what timezone the provided location falls in and REPLACE the
    timezone information on the provided datetime with THAT timezone, and
    return the result.

    Params:
        the_datetime :  a Python datetime object
        location :      A GeoDjango GEOS geometry for the location where
                        the_datetime is intended to be
    """

    tzinfo = timezone_for(location)

    if tzinfo != False:  # also type-check that the_datetime is a datetime or something we can replace the TZinfo on
        the_datetime = the_datetime.replace(tzinfo=None)  # strip the existing (if there) timezone out so we can re-localize
        return tzinfo.localize(the_datetime)

    logger.error("A timezone could not be found for %s" % location)
    return the_datetime


def time_for(the_datetime, location):
    """
    Determine what timezone the provided location falls in; convert the
    provided datetime into that timezone and return the result.
    """

    tzinfo = timezone_for(location)

    if tzinfo != False:
        return the_datetime.astimezone(tzinfo)
