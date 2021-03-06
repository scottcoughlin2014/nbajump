from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from firsttoscore.models import Game
from datetime import datetime
from requests import get
import json,pytz

__author__ = 'Giacomo Terreran <gqterre@gmail.com>'
__credits__ = ['Scott Coughlin <scottcoughlin2014@u.northwestern.edu>',
               'Kyle Kremer <kylekremer23@gmail.com>']

def update_schedule(_year):
    #_____________________________________________________________
    #get schedule json.
    
    print('Fetching {0} schedule.'.format(_year))
    schedule_url = 'http://data.nba.net/prod/v2/{0}/schedule.json'.format(_year)
    schedule_json=get(schedule_url).json()

    TODAY_UTC = timezone.now()
    
    update=0
    for el in schedule_json["league"]["standard"]:
        #___________________________________________
        # game["seasonStageId"]==1 -> pre-season
        # game["seasonStageId"]==2 -> regular-season
        # game["seasonStageId"]==3 -> exhibition game (like the All-Star Game)
        # game["seasonStageId"]==4 -> playoffs
        #___________________________________________
        
        # skipping games not played yet, and including only main-season.
        
        if el["seasonStageId"] in [1,3]:
            continue
    
    
        if not Game.objects.filter(game_id = el["gameId"]).exists():
           
            if update==0:
                print('Initializing {0} schedule.'.format(_year))
                update=1
            try:
                utc = pytz.utc.localize(datetime.strptime(el["startTimeUTC"], '%Y-%m-%dT%H:%M:%S.%fZ'))
            except:
                utc = pytz.utc.localize(datetime.strptime(el["startTimeUTC"], '%Y-%m-%d'))

            Game.objects.create(season=_year,game_id = el["gameId"] , game_utc = utc, game_date = el["startDateEastern"] , game_time = el["startTimeEastern"], stage = el["seasonStageId"] , tricode = el["gameUrlCode"].split('/')[1] , h_team = el["hTeam"]["teamId"] , a_team = el["vTeam"]["teamId"] , jumpers = [] , all_first_scorers = [] , all_first_shooters = [], jump_win = 0, team_first_score = 0, player_first_score = 0, last_update = TODAY_UTC)
        else:
            try:
                utc = pytz.utc.localize(datetime.strptime(el["startTimeUTC"], '%Y-%m-%dT%H:%M:%S.%fZ'))
            except:
                utc = pytz.utc.localize(datetime.strptime(el["startTimeUTC"], '%Y-%m-%d'))
        
            g=Game.objects.get(game_id = el["gameId"])
            if g.game_utc !=utc:
                print('{0} game (gameID: {1}) rescheduled from {2} to {3}.'.format(g.tricode,g.game_id,g.game_utc,utc))
                update=1
                g.game_utc = utc
                g.game_date = el["startDateEastern"]
                g.game_time = el["startTimeEastern"]
                g.last_update = TODAY_UTC
                g.save()

    if not update:
        print('No schedule update.')

class Command(BaseCommand):
    help = 'create schedule'

    def add_arguments(self, parser):
        parser.add_argument("--year",
                            help="Year for NBA data",
                            required=True, type=int)

    def handle(self, *args, **options):
        update_schedule(options["year"])
            






