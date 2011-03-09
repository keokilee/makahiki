from django.contrib import admin
from django import forms
from django.forms.util import ErrorList

from components.prizes.models import Prize, RaffleDeadline

admin.site.register(Prize)

class RaffleDeadlineAdminForm(forms.ModelForm):
  class Meta:
    model = RaffleDeadline
    
  def clean(self):
    """ 
      Validates the dates in the admin form.
    """
    # Data that has passed validation.
    cleaned_data = self.cleaned_data
    
    pub_date = cleaned_data.get("pub_date")
    end_date = cleaned_data.get("end_date")
    
    if pub_date >= end_date:
      self._errors["end_date"] = ErrorList([u"The end date must be after the pub date."])
      del cleaned_data["end_date"]
      
    return cleaned_data
    
class RaffleDeadlineAdmin(admin.ModelAdmin):
  form = RaffleDeadlineAdminForm
    
admin.site.register(RaffleDeadline, RaffleDeadlineAdmin)