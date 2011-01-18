from datetime import datetime

from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

#from django.contrib.auth.models import User



class BadgeAward(models.Model):
    # user = models.ForeignKey(User, related_name="badges_earned")

    # Following fields are required for using GenericForeignKey
    content_type = models.ForeignKey(ContentType, related_name="badges_earned")
    object_id = models.IntegerField()
    badge_recipient = generic.GenericForeignKey()

    awarded_at = models.DateTimeField(default=datetime.now)
    slug = models.CharField(max_length=255)
    level = models.IntegerField()
    
    def __getattr__(self, attr):
        return getattr(self._badge, attr)
    
    @property
    def badge(self):
        return self
    
    @property
    def _badge(self):
        from brabeion import badges
        return badges._registry[self.slug]
    
    @property
    def name(self):
        return self._badge.levels[self.level].name
    
    @property
    def description(self):
        return self._badge.levels[self.level].description
    
    @property
    def progress(self):
        return self._badge.progress(self.badge_recipient, self.level)
