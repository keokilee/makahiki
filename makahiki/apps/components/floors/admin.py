from django.contrib import admin
from components.floors.models import Dorm, Floor, Post

admin.site.register(Dorm)
admin.site.register(Floor)

class PostAdmin(admin.ModelAdmin):
  list_filter = ["style_class", "floor"]
  actions = ["delete_selected"]
  
  def delete_selected(self, request, queryset):
    for obj in queryset:
      obj.delete()
  delete_selected.short_description = "Delete the selected objects."
  
admin.site.register(Post, PostAdmin)