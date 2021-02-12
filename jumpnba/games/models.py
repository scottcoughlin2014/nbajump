from django.db import models
import json

# Create your models here.

class Game(models.Model):
    season = models.IntegerField()
    game_id = models.CharField(max_length=15)
    game_utc = models.DateTimeField(auto_now=0, auto_now_add=0)
    game_date = models.CharField(max_length=8)
    stage = models.IntegerField()
    tricode = models.CharField(max_length=6)
    h_team = models.CharField(max_length=15)
    a_team = models.CharField(max_length=15)
    jumpers = models.JSONField()
    jump_win = models.IntegerField()
    team_first_score = models.IntegerField()
    player_first_score = models.IntegerField()
    all_first_scorers = models.JSONField()
    all_first_shooters = models.JSONField()
    last_update = models.DateTimeField(auto_now=0, auto_now_add=0)
    
    def __str__(self):
        return 'Game_id: {} - {} - {})'.format(self.game_id,self.game_time, self.tricode)

