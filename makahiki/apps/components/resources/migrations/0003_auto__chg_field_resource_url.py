# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'Resource.url'
        db.alter_column('resources_resource', 'url', self.gf('django.db.models.fields.CharField')(max_length=300))
    
    
    def backwards(self, orm):
        
        # Changing field 'Resource.url'
        db.alter_column('resources_resource', 'url', self.gf('django.db.models.fields.URLField')(max_length=200))
    
    
    models = {
        'resources.resource': {
            'Meta': {'object_name': 'Resource'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'added_by': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 12, 18, 29, 26, 417695)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'media_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['resources.Topic']", 'symmetrical': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 12, 18, 29, 26, 417751)'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'resources.topic': {
            'Meta': {'object_name': 'Topic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['resources']
