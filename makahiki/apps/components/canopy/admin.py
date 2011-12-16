from django.contrib import admin

from components.canopy.models import Mission

class MissionAdmin(admin.ModelAdmin):
  # Automatically populates the slug field.
  prepopulated_fields = {"slug": ("name",)}
  
admin.site.register(Mission, MissionAdmin)