from django.contrib import admin
from components.makahiki_profiles.models import Profile

class ProfileAdmin(admin.ModelAdmin):
  search_fields = ["user__username", "user__email"]
  list_display = ['name', 'last_name', 'first_name',]
  
admin.site.register(Profile, ProfileAdmin)