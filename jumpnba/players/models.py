from django.db import models

# Create your models here.

class Player(models.Model):
    nba_id = models.IntegerField()
    fd_id = models.IntegerField(null=1)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    team_id = models.CharField(max_length=100)
    prev_teams = models.JSONField()
    is_jumper = models.BooleanField(default=0)
    jumps_jumped = models.IntegerField(default=0)
    jumps_won = models.IntegerField(default=0)
    elo_score = models.FloatField(default=1500)
    last_update = models.DateTimeField(auto_now=0, auto_now_add=0)
    
    def __str__(self):
        return '{} {} on {}'.format(self.first_name, self.last_name, self.team_id)
