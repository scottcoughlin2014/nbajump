from django.core.management.base import BaseCommand, CommandError
from firsttoscore.models import Team
from django.utils import timezone
from requests import get
import json

__author__ = 'Giacomo Terreran <gqterre@gmail.com>'
__credits__ = ['Scott Coughlin <scottcoughlin2014@u.northwestern.edu>',
               'Kyle Kremer <kylekremer23@gmail.com>']

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
#        team_url = 'http://data.nba.net/prod/v1/{0}/teams.json'.format(options["year"])
#        team_json=get(team_url).json()

        TODAY_UTC = timezone.now()

        if len(Team.objects.all())==0:

            print('Creating the team database')
            Team.objects.create(
                team_id = 1610612737,
                full_name ='Atlanta Hawks',
                tricode = 'ATL',
                names = ['Atlanta Hawks', 'ATL', 'Atlanta', 'Hawks'],
                colors = ['#e03a3e','#26282a'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612738,
                full_name ='Boston Celtics',
                tricode = 'BOS',
                names = ['Boston Celtics', 'BOS', 'Boston', 'Celtics'],
                colors = ['#008348','#ffffff'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612751,
                full_name ='Brooklyn Nets',
                tricode = 'BKN',
                names = ['Brooklyn Nets', 'BKN', 'Brooklyn', 'Nets'],
                colors = ['#000000','#ffffff'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612766,
                full_name ='Charlotte Hornets',
                tricode = 'CHA',
                names = ['Charlotte Hornets', 'CHA', 'Charlotte', 'Hornets'],
                colors = ['#00788c','#1d1160'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612741,
                full_name ='Chicago Bulls',
                tricode = 'CHI',
                names = ['Chicago Bulls', 'CHI', 'Chicago', 'Bulls'],
                colors = ['#ce1141','#ffffff'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612739,
                full_name ='Cleveland Cavaliers',
                tricode = 'CLE',
                names = ['Cleveland Cavaliers', 'CLE', 'Cleveland', 'Cavaliers'],
                colors = ['#6f263d','#041e42'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612742,
                full_name ='Dallas Mavericks',
                tricode = 'DAL',
                names = ['Dallas Mavericks', 'DAL', 'Dallas', 'Mavericks'],
                colors = ['#0053bc','#00285e'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612743,
                full_name ='Denver Nuggets',
                tricode = 'DEN',
                names = ['Denver Nuggets', 'DEN', 'Denver', 'Nuggets'],
                colors = ['#fec524','#244289'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612765,
                full_name ='Detroit Pistons',
                tricode = 'DET',
                names = ['Detroit Pistons', 'DET', 'Detroit', 'Pistons'],
                colors = ['#ffffff','#1d428a'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612744,
                full_name ='Golden State Warriors',
                tricode = 'GSW',
                names = ['Golden State Warriors', 'GSW', 'Golden State', 'Warriors'],
                colors = ['#fdb927','#006bb6'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612745,
                full_name ='Houston Rockets',
                tricode = 'HOU',
                names = ['Houston Rockets', 'HOU', 'Houston', 'Rockets'],
                colors = ['#ce1141','#ffffff'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612754,
                full_name ='Indiana Pacers',
                tricode = 'IND',
                names = ['Indiana Pacers', 'IND', 'Indiana', 'Pacers'],
                colors = ['#fdbb30','#002d62'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612746,
                full_name ='LA Clippers',
                tricode = 'LAC',
                names = ['LA Clippers', 'LAC', 'LA', 'Clippers'],
                colors = ['#ffffff','#1d428a'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612747,
                full_name ='Los Angeles Lakers',
                tricode = 'LAL',
                names = ['Los Angeles Lakers', 'LAL', 'Los Angeles', 'Lakers'],
                colors = ['#fdb927','#552583'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612763,
                full_name ='Memphis Grizzlies',
                tricode = 'MEM',
                names = ['Memphis Grizzlies', 'MEM', 'Memphis', 'Grizzlies'],
                colors = ['#5d76a9','#12173f'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612748,
                full_name ='Miami Heat',
                tricode = 'MIA',
                names = ['Miami Heat', 'MIA', 'Miami', 'Heat'],
                colors = ['#98002e','#000000'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612749,
                full_name ='Milwaukee Bucks',
                tricode = 'MIL',
                names = ['Milwaukee Bucks', 'MIL', 'Milwaukee', 'Bucks'],
                colors = ['#00471b','#ffffff'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612750,
                full_name ='Minnesota Timberwolves',
                tricode = 'MIN',
                names = ['Minnesota Timberwolves', 'MIN', 'Minnesota', 'Timberwolves'],
                colors = ['#236192','#0c2340'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612740,
                full_name ='New Orleans Pelicans',
                tricode = 'NOP',
                names = ['New Orleans Pelicans', 'NOP', 'New Orleans', 'Pelicans'],
                colors = ['#e31837','#002b5c'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612752,
                full_name ='New York Knicks',
                tricode = 'NYK',
                names = ['New York Knicks', 'NYK', 'New York', 'Knicks'],
                colors = ['#ffffff','#006bb6'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612760,
                full_name ='Oklahoma City Thunder',
                tricode = 'OKC',
                names = ['Oklahoma City Thunder', 'OKC', 'Oklahoma City', 'Thunder'],
                colors = ['#007ac1','#ffffff'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612753,
                full_name ='Orlando Magic',
                tricode = 'ORL',
                names = ['Orlando Magic', 'ORL', 'Orlando', 'Magic'],
                colors = ['#0077c0','#000000'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612755,
                full_name ='Philadelphia 76ers',
                tricode = 'PHI',
                names = ['Philadelphia 76ers', 'PHI', 'Philadelphia', '76ers'],
                colors = ['#ffffff','#006bb6'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612756,
                full_name ='Phoenix Suns',
                tricode = 'PHX',
                names = ['Phoenix Suns', 'PHX', 'Phoenix', 'Suns'],
                colors = ['#1d1160','#ffffff'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612757,
                full_name ='Portland Trail Blazers',
                tricode = 'POR',
                names = ['Portland Trail Blazers', 'POR', 'Portland', 'Trail Blazers'],
                colors = ['#000000','#ffffff'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612758,
                full_name ='Sacramento Kings',
                tricode = 'SAC',
                names = ['Sacramento Kings', 'SAC', 'Sacramento', 'Kings'],
                colors = ['#5a2b81','#ffffff'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612759,
                full_name ='San Antonio Spurs',
                tricode = 'SAS',
                names = ['San Antonio Spurs', 'SAS', 'San Antonio', 'Spurs'],
                colors = ['#c4ced4','#000000'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612761,
                full_name ='Toronto Raptors',
                tricode = 'TOR',
                names = ['Toronto Raptors', 'TOR', 'Toronto', 'Raptors'],
                colors = ['#ce1141','#ffffff'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612762,
                full_name ='Utah Jazz',
                tricode = 'UTA',
                names = ['Utah Jazz', 'UTA', 'Utah', 'Jazz'],
                colors = ['#f9a01b','#002b5c'],
                stats={},
                last_update = TODAY_UTC
            )

            Team.objects.create(
                team_id = 1610612764,
                full_name ='Washington Wizards',
                tricode = 'WAS',
                names = ['Washington Wizards', 'WAS', 'Washington', 'Wizards'],
                colors = ['#e31837','#002b5c'],
                stats={},
                last_update = TODAY_UTC
            )


        update=0
        for t in Team.objects.all():
            if str(options["year"]) not in t.stats:
                if update in [0]:
                    print('Initializing teams stats for {0}.'.format(options["year"]))
                    update=1
                t.stats[options["year"]]={'first_shot_three': 0, 'tip_off_won':0, 'scored_first_after_winning_tip_off':0, 'scored_first':0,'foul_first_defence':0, 'games_played':[], 'first_scorer':[], 'first_shooter':[], 'jumpers':[],'jumper_list':[], 'starters':[],'elo_off':1500,'elo_def':1500}
                t.save()

        if not update:
            print('No team update.')



