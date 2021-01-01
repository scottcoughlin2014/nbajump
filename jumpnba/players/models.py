from django.db import models

# Create your models here.

class Player(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    team_name = models.CharField(max_length=100)
    def __str__(self):
        return '{} {} on {}'.format(self.first_name, self.last_name, self.team_name)
