# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'Floor.wattdepot_host'
        db.add_column('kukui_cup_floors_floor', 'wattdepot_host', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)

        # Adding field 'Floor.wattdepot_source'
        db.add_column('kukui_cup_floors_floor', 'wattdepot_source', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Deleting field 'Floor.wattdepot_host'
        db.delete_column('kukui_cup_floors_floor', 'wattdepot_host')

        # Deleting field 'Floor.wattdepot_source'
        db.delete_column('kukui_cup_floors_floor', 'wattdepot_source')
    
    
    models = {
        'kukui_cup_floors.dorm': {
            'Meta': {'object_name': 'Dorm'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'kukui_cup_floors.floor': {
            'Meta': {'object_name': 'Floor'},
            'dorm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kukui_cup_floors.Dorm']"}),
            'floor_number': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'wattdepot_host': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'wattdepot_source': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['kukui_cup_floors']
