# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'Floor.description'
        db.delete_column('kukui_cup_floors_floor', 'description')

        # Deleting field 'Floor.creator'
        db.delete_column('kukui_cup_floors_floor', 'creator_id')

        # Deleting field 'Floor.created'
        db.delete_column('kukui_cup_floors_floor', 'created')

        # Deleting field 'Floor.slug'
        db.delete_column('kukui_cup_floors_floor', 'slug')

        # Deleting field 'Floor.name'
        db.delete_column('kukui_cup_floors_floor', 'name')
    
    
    def backwards(self, orm):
        
        # Adding field 'Floor.description'
        db.add_column('kukui_cup_floors_floor', 'description', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'Floor.creator'
        db.add_column('kukui_cup_floors_floor', 'creator', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='floor_created', to=orm['auth.User']), keep_default=False)

        # Adding field 'Floor.created'
        db.add_column('kukui_cup_floors_floor', 'created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now), keep_default=False)

        # Adding field 'Floor.slug'
        db.add_column('kukui_cup_floors_floor', 'slug', self.gf('django.db.models.fields.SlugField')(default='', max_length=50, unique=True, db_index=True), keep_default=False)

        # Adding field 'Floor.name'
        db.add_column('kukui_cup_floors_floor', 'name', self.gf('django.db.models.fields.CharField')(default='', max_length=80, unique=True), keep_default=False)
    
    
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['kukui_cup_floors']
