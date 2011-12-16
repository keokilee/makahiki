# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Topic'
        db.create_table('resources_topic', (
            ('topic', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('resources', ['Topic'])

        # Adding model 'Resource'
        db.create_table('resources_resource', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 7, 5, 14, 5, 22, 871501))),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 7, 5, 14, 5, 22, 871575))),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
            ('length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('media_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('added_by', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('resources', ['Resource'])

        # Adding M2M table for field topics on 'Resource'
        db.create_table('resources_resource_topics', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resource', models.ForeignKey(orm['resources.resource'], null=False)),
            ('topic', models.ForeignKey(orm['resources.topic'], null=False))
        ))
        db.create_unique('resources_resource_topics', ['resource_id', 'topic_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Topic'
        db.delete_table('resources_topic')

        # Deleting model 'Resource'
        db.delete_table('resources_resource')

        # Removing M2M table for field topics on 'Resource'
        db.delete_table('resources_resource_topics')
    
    
    models = {
        'resources.resource': {
            'Meta': {'object_name': 'Resource'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'added_by': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 5, 14, 5, 22, 871501)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'media_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['resources.Topic']", 'symmetrical': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 5, 14, 5, 22, 871575)'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'resources.topic': {
            'Meta': {'object_name': 'Topic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['resources']
