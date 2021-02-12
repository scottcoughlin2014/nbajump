from django.db import models
import json

# Create your models here.

class Team(models.Model):
    team_id = models.IntegerField()
    full_name = models.CharField(max_length=100)
    tricode = models.CharField(max_length=3)
    names = models.JSONField()
    stats = models.JSONField()
    last_update = models.DateTimeField(auto_now=0, auto_now_add=0)
    
    def __str__(self):
        return '{} ({})'.format(self.full_name, self.tricode)

