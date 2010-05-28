# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'CommonActivityUser'
        db.create_table('activities_commonactivityuser', (
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('approval_status', self.gf('django.db.models.fields.CharField')(default='unapproved', max_length=20)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('activities', ['CommonActivityUser'])

        # Adding model 'Commitment'
        db.create_table('activities_commitment', (
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('activities', ['Commitment'])

        # Adding model 'CommitmentMember'
        db.create_table('activities_commitmentmember', (
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('commitment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Commitment'])),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('activities', ['CommitmentMember'])

        # Adding model 'TextPromptQuestion'
        db.create_table('activities_textpromptquestion', (
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('activity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Activity'])),
        ))
        db.send_create_signal('activities', ['TextPromptQuestion'])

        # Adding model 'ConfirmationCode'
        db.create_table('activities_confirmationcode', (
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('activity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Activity'])),
        ))
        db.send_create_signal('activities', ['ConfirmationCode'])

        # Adding model 'Activity'
        db.create_table('activities_activity', (
            ('is_event', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('confirm_type', self.gf('django.db.models.fields.CharField')(default='text', max_length=20)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('confirm_prompt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')()),
            ('expire_date', self.gf('django.db.models.fields.DateField')()),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('event_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('pub_date', self.gf('django.db.models.fields.DateField')(default=datetime.date(2010, 5, 5))),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('activities', ['Activity'])

        # Adding model 'ActivityMember'
        db.create_table('activities_activitymember', (
            ('admin_comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('commonactivityuser_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['activities.CommonActivityUser'], unique=True, primary_key=True)),
            ('user_comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=1024, blank=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.TextPromptQuestion'], null=True, blank=True)),
            ('awarded', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('activity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Activity'])),
            ('response', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('activities', ['ActivityMember'])

        # Adding model 'Goal'
        db.create_table('activities_goal', (
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('activities', ['Goal'])

        # Adding model 'GoalMember'
        db.create_table('activities_goalmember', (
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tribes.Tribe'])),
            ('commonactivityuser_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['activities.CommonActivityUser'], unique=True, primary_key=True)),
            ('goal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Goal'])),
        ))
        db.send_create_signal('activities', ['GoalMember'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'CommonActivityUser'
        db.delete_table('activities_commonactivityuser')

        # Deleting model 'Commitment'
        db.delete_table('activities_commitment')

        # Deleting model 'CommitmentMember'
        db.delete_table('activities_commitmentmember')

        # Deleting model 'TextPromptQuestion'
        db.delete_table('activities_textpromptquestion')

        # Deleting model 'ConfirmationCode'
        db.delete_table('activities_confirmationcode')

        # Deleting model 'Activity'
        db.delete_table('activities_activity')

        # Deleting model 'ActivityMember'
        db.delete_table('activities_activitymember')

        # Deleting model 'Goal'
        db.delete_table('activities_goal')

        # Deleting model 'GoalMember'
        db.delete_table('activities_goalmember')
    
    
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
            'awarded': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "'CommitmentMember'"})
        },
        'activities.commitmentmember': {
            'Meta': {'object_name': 'CommitmentMember'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'commitment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.Commitment']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'activities.commonactivityuser': {
            'Meta': {'object_name': 'CommonActivityUser'},
            'approval_status': ('django.db.models.fields.CharField', [], {'default': "'unapproved'", 'max_length': '20'}),
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
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
