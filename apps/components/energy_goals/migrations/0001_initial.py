# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'EnergyGoal'
        db.create_table('energy_goals_energygoal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('voting_end_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('minimum_goal', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maximum_goal', self.gf('django.db.models.fields.IntegerField')(default=50)),
            ('goal_increments', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('default_goal', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('point_conversion', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('energy_goals', ['EnergyGoal'])

        # Adding model 'EnergyGoalVote'
        db.create_table('energy_goals_energygoalvote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('goal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['energy_goals.EnergyGoal'])),
            ('percent_reduction', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('energy_goals', ['EnergyGoalVote'])

        # Adding unique constraint on 'EnergyGoalVote', fields ['user', 'goal']
        db.create_unique('energy_goals_energygoalvote', ['user_id', 'goal_id'])

        # Adding model 'FloorEnergyGoal'
        db.create_table('energy_goals_floorenergygoal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('floor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['floors.Floor'])),
            ('goal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['energy_goals.EnergyGoal'])),
            ('percent_reduction', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('awarded', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('energy_goals', ['FloorEnergyGoal'])


    def backwards(self, orm):
        
        # Deleting model 'EnergyGoal'
        db.delete_table('energy_goals_energygoal')

        # Deleting model 'EnergyGoalVote'
        db.delete_table('energy_goals_energygoalvote')

        # Removing unique constraint on 'EnergyGoalVote', fields ['user', 'goal']
        db.delete_unique('energy_goals_energygoalvote', ['user_id', 'goal_id'])

        # Deleting model 'FloorEnergyGoal'
        db.delete_table('energy_goals_floorenergygoal')


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
        'energy_goals.energygoal': {
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
        'energy_goals.energygoalvote': {
            'Meta': {'unique_together': "(('user', 'goal'),)", 'object_name': 'EnergyGoalVote'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'goal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['energy_goals.EnergyGoal']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent_reduction': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'energy_goals.floorenergygoal': {
            'Meta': {'object_name': 'FloorEnergyGoal'},
            'awarded': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'floor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['floors.Floor']"}),
            'goal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['energy_goals.EnergyGoal']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent_reduction': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
        }
    }

    complete_apps = ['energy_goals']
