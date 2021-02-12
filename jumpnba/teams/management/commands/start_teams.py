from django.core.management.base import BaseCommand, CommandError
from teams.models import Team
from django.utils import timezone
from requests import get
import sys,json

class Command(BaseCommand):
    help = 'start teams database'

    def add_arguments(self, parser):
        parser.add_argument("--year",
                            help="Year for NBA data",
                            required=True, type=int)

    def get_names(self,_team):
        out=[]
        for id in ["fullName","tricode","city","nickname"]:
            out.append(_team[id])
        return out

    def handle(self, *args, **options):
        #_____________________________________________________________
        #get teams json.
        team_url = 'http://data.nba.net/prod/v1/{0}/teams.json'.format(options["year"])
        team_json=get(team_url).json()

        TODAY_UTC = timezone.now()

        update=0
        for el in team_json["league"]["standard"]:
            if not Team.objects.filter(team_id = el["teamId"]).exists():
                
                if not update:
                    print('Fetching teams info.')
                    update=1
                
                Team.objects.create(team_id = el["teamId"] , full_name = el["fullName"], tricode = el["tricode"] , names = self.get_names(el) , stats={} , last_update = TODAY_UTC)
            t=Team.objects.get(team_id = el["teamId"])
            if str(options["year"]) not in t.stats:
                if update in [0,1]:
                    print('Initializing teams stats for {0}.'.format(options["year"]))
                    update=2
                t.stats[options["year"]]={'first_shot_three': 0, 'tip_off_won':0, 'scored_first_after_winning_tip_off':0, 'scored_first':0,'foul_first_defence':0, 'games_played':[], 'first_scorer':[], 'first_shooter':[], 'jumpers':[],'jumper_list':[], 'starters':[]}
                t.save()

        if not update:
            print('No team update.')



