from django import forms

from floors.models import Floor
from makahiki_base import get_floor_label

class EnergyDataSelectForm(forms.Form):
  floor = forms.ModelChoiceField(
              queryset=Floor.objects.all().order_by("dorm__name", "number"),
              label="Pick a %s" % get_floor_label().lower(),
              empty_label=None,
          )
  