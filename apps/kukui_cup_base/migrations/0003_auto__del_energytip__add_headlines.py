# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting model 'EnergyTip'
        db.delete_table('kukui_cup_base_energytip')

        # Adding model 'Headlines'
        db.create_table('kukui_cup_base_headlines', (
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('kukui_cup_base', ['Headlines'])
    
    
    def backwards(self, orm):
        
        # Adding model 'EnergyTip'
        db.create_table('kukui_cup_base_energytip', (
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('kukui_cup_base', ['EnergyTip'])

        # Deleting model 'Headlines'
        db.delete_table('kukui_cup_base_headlines')
    
    
    models = {
        'kukui_cup_base.article': {
            'Meta': {'object_name': 'Article'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'kukui_cup_base.headlines': {
            'Meta': {'object_name': 'Headlines'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['kukui_cup_base']
