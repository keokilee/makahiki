# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Article'
        db.create_table('makahiki_base_article', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('makahiki_base', ['Article'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Article'
        db.delete_table('makahiki_base_article')
    
    
    models = {
        'makahiki_base.article': {
            'Meta': {'object_name': 'Article'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        }
    }
    
    complete_apps = ['makahiki_base']
