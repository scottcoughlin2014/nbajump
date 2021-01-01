from django.db import models
from players.models import Player

# Create your models here.
class FanDuelOdds(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    first_to_score_odds = models.FloatField()
    date = models.DateTimeField()
    def __str__(self):
        return '{} odds {} on {}'.format(self.player, self.first_to_score_odds, self.date)

class FirstScorer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    number_of_times = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return '{} scores {} times'.format(self.player, self.number_of_times)
