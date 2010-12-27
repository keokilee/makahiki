# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'Floor.floor_number'
        db.delete_column('floors_floor', 'floor_number')

        # Adding field 'Floor.number'
        db.add_column('floors_floor', 'number', self.gf('django.db.models.fields.CharField')(default='3-4', max_length=10), keep_default=False)

        # Adding field 'Floor.slug'
        db.add_column('floors_floor', 'slug', self.gf('django.db.models.fields.CharField')(default='3-4', max_length=10, blank=True), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Adding field 'Floor.floor_number'
        db.add_column('floors_floor', 'floor_number', self.gf('django.db.models.fields.IntegerField')(default=3), keep_default=False)

        # Deleting field 'Floor.number'
        db.delete_column('floors_floor', 'number')

        # Deleting field 'Floor.slug'
        db.delete_column('floors_floor', 'slug')
    
    
    models = {
        'floors.dorm': {
            'Meta': {'object_name': 'Dorm'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'floors.floor': {
            'Meta': {'object_name': 'Floor'},
            'chart_dorm': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'chart_floor': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'chart_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'dorm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['floors.Dorm']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        }
    }
    
    complete_apps = ['floors']
