from django.db import models
from players.models import Player
from datetime import date


# Create your models here.
class FanDuelOdds(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    first_to_score_odds = models.FloatField()
    date = models.DateTimeField()
