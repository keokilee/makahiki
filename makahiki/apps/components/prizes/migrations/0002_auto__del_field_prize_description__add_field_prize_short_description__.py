# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Rename field 'Prize.description'
        db.rename_column('prizes_prize', 'description', 'short_description')

        # Adding field 'Prize.long_description'
        db.add_column('prizes_prize', 'long_description', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)
        
        # Copy short description to long description.
        if not db.dry_run:
          for prize in orm.Prize.objects.all():
            prize.long_description = prize.short_description
            prize.save()

    def backwards(self, orm):
        
        # Rename field 'Prize.short_description'
        db.rename_column('prizes_prize', 'short_description', 'description')

        # Deleting field 'Prize.long_description'
        db.delete_column('prizes_prize', 'long_description')


    models = {
        'prizes.prize': {
            'Meta': {'unique_together': "(('round_name', 'award_to', 'competition_type'),)", 'object_name': 'Prize'},
            'award_to': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'competition_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '1024', 'blank': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {}),
            'round_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'short_description': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['prizes']
