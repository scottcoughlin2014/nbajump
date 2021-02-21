from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from firsttoscore.models import Player
from requests import get

__author__ = 'Giacomo Terreran <gqterre@gmail.com>'
__credits__ = ['Scott Coughlin <scottcoughlin2014@u.northwestern.edu>',
               'Kyle Kremer <kylekremer23@gmail.com>']

def update_players(_year):
    no_update=1
    #______________________________________________________
    #get players json.
    player_url = 'http://data.nba.net/prod/v1/{0}/players.json'.format(_year)
    player_json=get(player_url).json()

    TODAY_UTC = timezone.now()

    for el in player_json["league"]["standard"]:
        #if the player does not exist it will be added
        if not Player.objects.filter(nba_id = el["personId"]).exists():
            Player.objects.create(nba_id = el["personId"], first_name = el["firstName"], last_name = el["lastName"], team_id = el["teamId"], prev_teams = el["teams"], last_update = TODAY_UTC)
            print('{} {} added.'.format(el["firstName"] , el["lastName"]))
            no_update=0
        #if exists, check if he changed team.
        else    :
            p=Player.objects.get(nba_id = el["personId"])
            if len(p.prev_teams)<len(el["teams"]):
                p.team_id = el["teams"][-1]["teamId"]
                p.prev_teams = el["teams"]
                p.last_update = TODAY_UTC
                p.save()
                print('{} {} changed team.'.format(p.first_name,p.last_name))
                no_update=0
    if no_update:
        print('No update')

class Command(BaseCommand):
    help = 'update player database'

    def add_arguments(self, parser):
        parser.add_argument("--year",
                            help="Year for NBA data",
                            required=True, type=int)

    def handle(self, *args, **options):
        
        update_players(options["year"])




