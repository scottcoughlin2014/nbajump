import requests
import pandas as pd
from pandas.io.json import json_normalize
from functools import reduce
from datetime import date
import datetime

from django.core.management.base import BaseCommand, CommandError
from firsttoscore.models import Team, Game

def parse_data(jsonData):
    results_df = pd.DataFrame()
    for alpha in jsonData['events']:
        print ('Gathering %s data: %s @ %s' %(alpha['sportname'],alpha['participantname_away'],alpha['participantname_home']))
        alpha_df = json_normalize(alpha).drop('markets',axis=1)
        results_df = results_df.append(alpha_df)

    return results_df

def parse_individual_game_data(jsonData, hometeam=None, awayteam=None):
    results_df = pd.DataFrame()
    if "eventmarketgroups" not in jsonData.keys():
        return results_df

    counter = 0
    all_team_names = []
    all_odds = []
    for k in jsonData["eventmarketgroups"][-1]["markets"]:
        if k["name"] == "Team to Score First":
            teams = []
            for idx, team_score_first_odds in enumerate(k["selections"]):
                all_team_names.append(team_score_first_odds["name"])
                all_odds.append(team_score_first_odds["currentpriceup"]/team_score_first_odds["currentpricedown"])
    results_df = pd.DataFrame({"away_team_name" : all_team_names[0], "a_odds" : all_odds[0], "home_team_name" : all_team_names[1], "h_odds" : all_odds[1]}, index=[0])
    return results_df

def clean_team_name(x):
    if x == "Los Angeles Clippers":
        return "LA Clippers"
    else:
        return x

class Command(BaseCommand):
    help = 'Command to update or make new GRB for the bright.ciera.northwestern.edu webserver'

#    def add_arguments(self, parser):
#        parser.add_argument("--json-file", required=True)

    def handle(self, *args, **options):
        jsonData_fanduel_nba = requests.get('https://sportsbook.fanduel.com/cache/psmg/US/55978.3.json').json()

        nba = parse_data(jsonData_fanduel_nba)

        all_results_df = pd.DataFrame()
        for gameid, hometeam, awayteam in zip(nba["idfoevent"], nba["participantname_home"], nba["participantname_away"]):
            jsonData_fanduel_nba = requests.get("https://sportsbook.fanduel.com/cache/psevent/US/1/false/{0}.json".format(gameid)).json()
            odds = parse_individual_game_data(jsonData_fanduel_nba, hometeam=hometeam, awayteam=awayteam)
            odds["gameid"] = gameid
            odds["tsstart"] = jsonData_fanduel_nba["tsstart"]
            all_results_df = all_results_df.append(odds)

        all_results_df["home_team_name"] = all_results_df["home_team_name"].apply(clean_team_name)
        all_results_df["away_team_name"] = all_results_df["away_team_name"].apply(clean_team_name)

        for row_id, row in all_results_df.iterrows():
            h_team = Team.objects.get(full_name=row["home_team_name"])
            a_team = Team.objects.get(full_name=row["away_team_name"])
            # get the game info
            game = Game.objects.get(h_team=h_team.team_id, a_team=a_team.team_id, game_date=datetime.datetime.now().strftime("%Y%m%d"))
            game.h_odds = row["h_odds"]
            game.a_odds = row["a_odds"]
            game.save()
