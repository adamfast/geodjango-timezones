# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Timezone'
        db.create_table('timezones_timezone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tzid', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('mpoly', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('timezones', ['Timezone'])


    def backwards(self, orm):
        
        # Deleting model 'Timezone'
        db.delete_table('timezones_timezone')


    models = {
        'timezones.timezone': {
            'Meta': {'object_name': 'Timezone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mpoly': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'tzid': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['timezones']
