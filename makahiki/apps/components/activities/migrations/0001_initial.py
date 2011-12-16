# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CommonActivityUser'
        db.create_table('activities_commonactivityuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('approval_status', self.gf('django.db.models.fields.CharField')(default='unapproved', max_length=20)),
            ('award_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('submission_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('activities', ['CommonActivityUser'])

        # Adding model 'Category'
        db.create_table('activities_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('activities', ['Category'])

        # Adding model 'ActivityBase'
        db.create_table('activities_activitybase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Category'], null=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1000)),
            ('depends_on', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('activities', ['ActivityBase'])

        # Adding model 'Commitment'
        db.create_table('activities_commitment', (
            ('activitybase_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['activities.ActivityBase'], unique=True, primary_key=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('activities', ['Commitment'])

        # Adding model 'Activity'
        db.create_table('activities_activity', (
            ('activitybase_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['activities.ActivityBase'], unique=True, primary_key=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('point_value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('point_range_start', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('point_range_end', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pub_date', self.gf('django.db.models.fields.DateField')(default=datetime.date(2011, 2, 17))),
            ('expire_date', self.gf('django.db.models.fields.DateField')()),
            ('confirm_type', self.gf('django.db.models.fields.CharField')(default='text', max_length=20)),
            ('confirm_prompt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('event_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('activities', ['Activity'])

        # Adding model 'CommitmentMember'
        db.create_table('activities_commitmentmember', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('commitment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Commitment'])),
            ('award_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('completion_date', self.gf('django.db.models.fields.DateField')()),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('activities', ['CommitmentMember'])

        # Adding model 'TextPromptQuestion'
        db.create_table('activities_textpromptquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('activity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Activity'])),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('activities', ['TextPromptQuestion'])

        # Adding model 'ConfirmationCode'
        db.create_table('activities_confirmationcode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('activity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Activity'])),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('activities', ['ConfirmationCode'])

        # Adding model 'ActivityMember'
        db.create_table('activities_activitymember', (
            ('commonactivityuser_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['activities.CommonActivityUser'], unique=True, primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('activity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.Activity'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activities.TextPromptQuestion'], null=True, blank=True)),
            ('response', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('admin_comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user_comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=1024, blank=True)),
            ('points_awarded', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('activities', ['ActivityMember'])


    def backwards(self, orm):
        
        # Deleting model 'CommonActivityUser'
        db.delete_table('activities_commonactivityuser')

        # Deleting model 'Category'
        db.delete_table('activities_category')

        # Deleting model 'ActivityBase'
        db.delete_table('activities_activitybase')

        # Deleting model 'Commitment'
        db.delete_table('activities_commitment')

        # Deleting model 'Activity'
        db.delete_table('activities_activity')

        # Deleting model 'CommitmentMember'
        db.delete_table('activities_commitmentmember')

        # Deleting model 'TextPromptQuestion'
        db.delete_table('activities_textpromptquestion')

        # Deleting model 'ConfirmationCode'
        db.delete_table('activities_confirmationcode')

        # Deleting model 'ActivityMember'
        db.delete_table('activities_activitymember')


    models = {
        'activities.activity': {
            'Meta': {'object_name': 'Activity', '_ormbases': ['activities.ActivityBase']},
            'activitybase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['activities.ActivityBase']", 'unique': 'True', 'primary_key': 'True'}),
            'confirm_prompt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'confirm_type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'expire_date': ('django.db.models.fields.DateField', [], {}),
            'point_range_end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'point_range_start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(2011, 2, 17)'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['activities.ActivityMember']", 'symmetrical': 'False'})
        },
        'activities.activitybase': {
            'Meta': {'object_name': 'ActivityBase'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.Category']", 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'depends_on': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        'activities.activitymember': {
            'Meta': {'object_name': 'ActivityMember', '_ormbases': ['activities.CommonActivityUser']},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.Activity']"}),
            'admin_comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'commonactivityuser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['activities.CommonActivityUser']", 'unique': 'True', 'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '1024', 'blank': 'True'}),
            'points_awarded': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.TextPromptQuestion']", 'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'user_comment': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'activities.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'activities.commitment': {
            'Meta': {'object_name': 'Commitment', '_ormbases': ['activities.ActivityBase']},
            'activitybase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['activities.ActivityBase']", 'unique': 'True', 'primary_key': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['activities.CommitmentMember']", 'symmetrical': 'False'})
        },
        'activities.commitmentmember': {
            'Meta': {'object_name': 'CommitmentMember'},
            'award_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'commitment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.Commitment']"}),
            'completion_date': ('django.db.models.fields.DateField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'activities.commonactivityuser': {
            'Meta': {'object_name': 'CommonActivityUser'},
            'approval_status': ('django.db.models.fields.CharField', [], {'default': "'unapproved'", 'max_length': '20'}),
            'award_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        'activities.confirmationcode': {
            'Meta': {'object_name': 'ConfirmationCode'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activities.Activity']"}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
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
        'makahiki_base.like': {
            'Meta': {'object_name': 'Like'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'floor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['floors.Floor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['activities']
