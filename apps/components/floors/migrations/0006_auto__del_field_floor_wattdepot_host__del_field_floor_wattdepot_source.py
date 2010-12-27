# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'Floor.wattdepot_host'
        db.delete_column('floors_floor', 'wattdepot_host')

        # Deleting field 'Floor.wattdepot_source'
        db.delete_column('floors_floor', 'wattdepot_source')

        # Adding field 'Floor.chart_url'
        db.add_column('floors_floor', 'chart_url', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)

        # Adding field 'Floor.chart_floor'
        db.add_column('floors_floor', 'chart_floor', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Adding field 'Floor.wattdepot_host'
        db.add_column('floors_floor', 'wattdepot_host', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)

        # Adding field 'Floor.wattdepot_source'
        db.add_column('floors_floor', 'wattdepot_source', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)

        # Deleting field 'Floor.chart_url'
        db.delete_column('floors_floor', 'chart_url')

        # Deleting field 'Floor.chart_floor'
        db.delete_column('floors_floor', 'chart_floor')
    
    
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
            'chart_floor': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'chart_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'dorm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['floors.Dorm']"}),
            'floor_number': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['floors']
