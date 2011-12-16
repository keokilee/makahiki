# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MakahikiLog'
        db.create_table('analytics_makahikilog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('level', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('request_time', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('remote_user', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('request', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('post_content', self.gf('django.db.models.fields.CharField')(max_length=4000)),
        ))
        db.send_create_signal('analytics', ['MakahikiLog'])


    def backwards(self, orm):
        
        # Deleting model 'MakahikiLog'
        db.delete_table('analytics_makahikilog')


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
        },
        'analytics.makahikilog': {
            'Meta': {'object_name': 'MakahikiLog'},
            'host': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'post_content': ('django.db.models.fields.CharField', [], {'max_length': '4000'}),
            'remote_user': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'request': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'request_time': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['analytics']
