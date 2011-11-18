# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'MakahikiLog.post_content'
        db.alter_column('analytics_makahikilog', 'post_content', self.gf('django.db.models.fields.TextField')())


    def backwards(self, orm):
        
        # Changing field 'MakahikiLog.post_content'
        db.alter_column('analytics_makahikilog', 'post_content', self.gf('django.db.models.fields.CharField')(max_length=4000))


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
            'post_content': ('django.db.models.fields.TextField', [], {}),
            'remote_user': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'request': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'request_time': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['analytics']
