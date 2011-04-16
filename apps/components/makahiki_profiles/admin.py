from django.contrib import admin
from components.makahiki_profiles.models import Profile

class ProfileAdmin(admin.ModelAdmin):
  search_fields = ["user__username", "user__email"]
  
admin.site.register(Profile, ProfileAdmin)