# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'Resource.length'
        db.alter_column('resources_resource', 'length', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True))
    
    
    def backwards(self, orm):
        
        # Changing field 'Resource.length'
        db.alter_column('resources_resource', 'length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True))
    
    
    models = {
        'resources.resource': {
            'Meta': {'object_name': 'Resource'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'added_by': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 12, 18, 25, 31, 472547)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'media_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['resources.Topic']", 'symmetrical': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 12, 18, 25, 31, 472605)'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'resources.topic': {
            'Meta': {'object_name': 'Topic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['resources']
