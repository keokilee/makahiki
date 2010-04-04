from activities.models import Activity, Commitment, ActivityMember, CommitmentMember
from django.contrib import admin
from django.forms import ModelForm
from django.forms.util import ErrorList
  
class ActivityAdminForm(ModelForm):
  class Meta:
    model = Activity
    
  def clean(self):
    """Checks that an event has an event date."""
    
    cleaned_data = self.cleaned_data
    is_event = cleaned_data.get("is_event")
    event_date = cleaned_data.get("event_date")
    has_date = cleaned_data.has_key("event_date") #Check if this is in the data dict.
    
    if is_event and has_date and not event_date:
      self._errors["event_date"] = ErrorList([u"Events require an event date."])
      del cleaned_data["is_event"]
      del cleaned_data["event_date"]
      
    return cleaned_data

class ActivityAdmin(admin.ModelAdmin):
  form = ActivityAdminForm
  
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityMember)
admin.site.register(Commitment)
