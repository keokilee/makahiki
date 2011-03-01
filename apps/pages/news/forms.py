from django import forms
  
class WallForm(forms.Form):
  post = forms.CharField(widget=forms.Textarea, initial="What's on your mind?")
  
class PopularTasksForm(forms.Form):
  TASK_TYPES = (
    ("activity", "Activities"),
    ("commitment", "Commitments"),
    ("event", "Events"),
    ("survey", "Surveys"),
    ("excursion", "Excursions"),
  )
  activity_type = forms.ChoiceField(choices=TASK_TYPES)