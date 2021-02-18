from django.db import models
#from players.models import Player

# Create your models here.
#class FanDuelOdds(models.Model):
#    player = models.ForeignKey(Player, on_delete=models.CASCADE)
#    first_to_score_odds = models.FloatField()
#    date = models.DateTimeField()
#    def __str__(self):
#        return '{} odds {} on {}'.format(self.player, self.first_to_score_odds, self.date)
#
#class FirstScorer(models.Model):
#    player = models.ForeignKey(Player, on_delete=models.CASCADE)
#    number_of_times = models.IntegerField(null=True, blank=True)
#    def __str__(self):
#        return '{} scores {} times'.format(self.player, self.number_of_times)

class Game(models.Model):
    season = models.IntegerField()
    game_id = models.CharField(max_length=15)
    game_utc = models.DateTimeField(auto_now=0, auto_now_add=0)
    game_date = models.CharField(max_length=8)
    game_time = models.CharField(max_length=8)
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
        return 'Game_id: {} - {} {} - {}'.format(self.game_id,self.game_date,self.game_time, self.tricode)

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

class Team(models.Model):
    team_id = models.IntegerField()
    full_name = models.CharField(max_length=100)
    tricode = models.CharField(max_length=3)
    names = models.JSONField()
    stats = models.JSONField()
    last_update = models.DateTimeField(auto_now=0, auto_now_add=0)
    
    def __str__(self):
        return '{} ({})'.format(self.full_name, self.tricode)
