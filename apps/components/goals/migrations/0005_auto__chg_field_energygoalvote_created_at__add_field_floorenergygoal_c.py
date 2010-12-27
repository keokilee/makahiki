# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'EnergyGoalVote.created_at'
        db.alter_column('goals_energygoalvote', 'created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Adding field 'FloorEnergyGoal.created_at'
        db.add_column('goals_floorenergygoal', 'created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.date(2010, 9, 12), blank=True), keep_default=False)

        # Adding field 'FloorEnergyGoal.updated_at'
        db.add_column('goals_floorenergygoal', 'updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.date(2010, 9, 12), blank=True), keep_default=False)

        # Changing field 'EnergyGoal.created_at'
        db.alter_column('goals_energygoal', 'created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'EnergyGoal.updated_at'
        db.alter_column('goals_energygoal', 'updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True))
    
    
    def backwards(self, orm):
        
        # Changing field 'EnergyGoalVote.created_at'
        db.alter_column('goals_energygoalvote', 'created_at', self.gf('django.db.models.fields.DateTimeField')())

        # Deleting field 'FloorEnergyGoal.created_at'
        db.delete_column('goals_floorenergygoal', 'created_at')

        # Deleting field 'FloorEnergyGoal.updated_at'
        db.delete_column('goals_floorenergygoal', 'updated_at')

        # Changing field 'EnergyGoal.created_at'
        db.alter_column('goals_energygoal', 'created_at', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'EnergyGoal.updated_at'
        db.alter_column('goals_energygoal', 'updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True))
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'floors.dorm': {
            'Meta': {'object_name': 'Dorm'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '20', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'floors.floor': {
            'Meta': {'object_name': 'Floor'},
            'dorm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['floors.Dorm']"}),
            'floor_identifier': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '10', 'db_index': 'True'})
        },
        'goals.energygoal': {
            'Meta': {'object_name': 'EnergyGoal'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_goal': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'goal_increments': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_goal': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'minimum_goal': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'point_conversion': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'voting_end_date': ('django.db.models.fields.DateField', [], {})
        },
        'goals.energygoalvote': {
            'Meta': {'unique_together': "(('user', 'goal'),)", 'object_name': 'EnergyGoalVote'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'goal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['goals.EnergyGoal']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent_reduction': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'goals.floorenergygoal': {
            'Meta': {'object_name': 'FloorEnergyGoal'},
            'awarded': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'floor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['floors.Floor']"}),
            'goal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['goals.EnergyGoal']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent_reduction': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['goals']
