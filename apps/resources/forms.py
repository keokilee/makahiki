from django import forms

from resources.models import Topic
  
class TopicChoiceField(forms.ModelMultipleChoiceField):
  """Custom choice field to customize the label for each topic."""
  def label_from_instance(self, obj):
    return "%s (%d)" % (obj.topic, obj.resource_set.count())

class TopicSelectForm(forms.Form):
  """Form for selecting topics in the resource list."""
  topics = TopicChoiceField(
      label="",
      queryset=Topic.objects,
      widget=forms.CheckboxSelectMultiple,
      initial=[topic.pk for topic in Topic.objects.all()],
  )
  
class ViewAllForm(forms.Form):
  """Form for displaying all resources."""
  topics = forms.ModelMultipleChoiceField(
      queryset=Topic.objects,
      widget=forms.MultipleHiddenInput, 
      initial=[topic.pk for topic in Topic.objects.all()],
  )
  