# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'CommonActivityUser.awarded'
        db.add_column('activities_commonactivityuser', 'awarded', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Deleting field 'ActivityMember.awarded'
        db.delete_column('activities_activitymember', 'awarded')
    
    
    def backwards(self, orm):
        
        # Deleting field 'CommonActivityUser.awarded'
        db.delete_column('activities_commonactivityuser', 'awarded')

        # Adding field 'ActivityMember.awarded'
        db.add_column('activities_activitymember', 'awarded', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)
    
    
    models = {
        'activities.activity': {
            'Meta': {'object_name': 'Activity'},
            'confirm_prompt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'confirm_type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'expire_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_event': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {}),
            'pub_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(2010, 5, 5)'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "'ActivityMember'"})
        },
        'activities.activitymember': {
            'Meta': {'object_name': 'ActivityMember', '_ormbases': ['activities.CommonActivityUser']},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.Activity']"}),
            'admin_comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'commonactivityuser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['activities.CommonActivityUser']", 'unique': 'True', 'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '1024', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.TextPromptQuestion']", 'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'user_comment': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'activities.commitment': {
            'Meta': {'object_name': 'Commitment'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "'CommitmentMember'"})
        },
        'activities.commitmentmember': {
            'Meta': {'object_name': 'CommitmentMember'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'commitment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.Commitment']"}),
            'completion_date': ('django.db.models.fields.DateField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'activities.commonactivityuser': {
            'Meta': {'object_name': 'CommonActivityUser'},
            'approval_status': ('django.db.models.fields.CharField', [], {'default': "'unapproved'", 'max_length': '20'}),
            'awarded': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'activities.confirmationcode': {
            'Meta': {'object_name': 'ConfirmationCode'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.Activity']"}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'activities.goal': {
            'Meta': {'object_name': 'Goal'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tribes.Tribe']", 'through': "'GoalMember'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'activities.goalmember': {
            'Meta': {'object_name': 'GoalMember', '_ormbases': ['activities.CommonActivityUser']},
            'commonactivityuser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['activities.CommonActivityUser']", 'unique': 'True', 'primary_key': 'True'}),
            'goal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.Goal']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tribes.Tribe']"})
        },
        'activities.textpromptquestion': {
            'Meta': {'object_name': 'TextPromptQuestion'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.Activity']"}),
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tribes.tribe': {
            'Meta': {'object_name': 'Tribe'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tribe_created'", 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tribes'", 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        }
    }
    
    complete_apps = ['activities']
