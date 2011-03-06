# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Prize'
        db.create_table('prizes_prize', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=1024, blank=True)),
            ('round_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('award_to', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('award_criteria', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('prizes', ['Prize'])

        # Adding unique constraint on 'Prize', fields ['round_name', 'award_to', 'award_criteria']
        db.create_unique('prizes_prize', ['round_name', 'award_to', 'award_criteria'])


    def backwards(self, orm):
        
        # Deleting model 'Prize'
        db.delete_table('prizes_prize')

        # Removing unique constraint on 'Prize', fields ['round_name', 'award_to', 'award_criteria']
        db.delete_unique('prizes_prize', ['round_name', 'award_to', 'award_criteria'])


    models = {
        'prizes.prize': {
            'Meta': {'unique_together': "(('round_name', 'award_to', 'award_criteria'),)", 'object_name': 'Prize'},
            'award_criteria': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'award_to': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '1024', 'blank': 'True'}),
            'round_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['prizes']
