from django.contrib.gis import admin
from timezones.models import *


class TimezoneAdmin(admin.OSMGeoAdmin):
    list_display = ('tzid',)
    search_fields = ('tzid',)


admin.site.register(Timezone, TimezoneAdmin)
