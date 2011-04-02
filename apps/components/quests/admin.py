from django.contrib import admin
from components.quests.models import Quest

class QuestAdmin(admin.ModelAdmin):
  prepopulated_fields = {"quest_slug": ("name",)}
  
admin.site.register(Quest, QuestAdmin)