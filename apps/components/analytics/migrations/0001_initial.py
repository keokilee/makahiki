# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ApacheLog'
        db.create_table('analytics_apachelog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('remote_user', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('request_time', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('request', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('response_size', self.gf('django.db.models.fields.IntegerField')()),
            ('referral', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('agent', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('analytics', ['ApacheLog'])


    def backwards(self, orm):
        
        # Deleting model 'ApacheLog'
        db.delete_table('analytics_apachelog')


    models = {
        'analytics.apachelog': {
            'Meta': {'object_name': 'ApacheLog'},
            'agent': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referral': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'remote_user': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'request': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'request_time': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'response_size': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['analytics']
