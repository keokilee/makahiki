from django.db import models

class ApacheLog(models.Model):
    host = models.CharField(max_length=50)
    remote_user = models.CharField(max_length=100, blank=True, null=True)
    request_time = models.CharField(max_length=100)
    request = models.CharField(max_length=10)
    url = models.CharField(max_length=1000)
    status = models.IntegerField()
    response_size = models.IntegerField()
    referral = models.CharField(max_length=1000)
    agent = models.CharField(max_length=300)

class MakahikiLog(models.Model):
    level = models.CharField(max_length=10)
    request_time = models.CharField(max_length=100)
    host = models.CharField(max_length=50)
    remote_user = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    request = models.CharField(max_length=10)
    url = models.CharField(max_length=1000)
    status = models.IntegerField()
    post_content = models.TextField()
