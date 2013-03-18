from django.contrib.gis.db import models


class Timezone(models.Model):
    tzid = models.CharField(max_length=128)
    mpoly = models.MultiPolygonField()

    objects = models.GeoManager()

    def __unicode__(self):
        return self.tzid
