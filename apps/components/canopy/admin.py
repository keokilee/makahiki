from django.contrib import admin

from components.canopy.models import Quest

class QuestAdmin(admin.ModelAdmin):
  # Automatically populates the slug field.
  prepopulated_fields = {"slug": ("name",)}
  
admin.site.register(Quest, QuestAdmin)