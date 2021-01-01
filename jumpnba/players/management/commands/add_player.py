import requests
import pandas as pd
from pandas.io.json import json_normalize
from functools import reduce
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from players.models import Player
from firsttoscore.models import FanDuelOdds

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
    all_first_names = []
    all_last_names = []
    all_team_names = []
    all_odds = []
    for k in jsonData["eventmarketgroups"][-1]["markets"]:
        if k["name"] == "First Basket":
            for k1 in k["selections"]:
                if counter >4:
                    all_team_names.append(hometeam)
                    all_odds.append(k1["currentpriceup"]/k1["currentpricedown"])
                    all_first_names.append(k1["name"].split()[0])
                    all_last_names.append(k1["name"].split()[1])
                else:
                    all_team_names.append(awayteam)
                    all_odds.append(k1["currentpriceup"]/k1["currentpricedown"])
                    all_first_names.append(k1["name"].split()[0])
                    all_last_names.append(k1["name"].split()[1])
                counter+=1
    results_df = pd.DataFrame({"first_name" : all_first_names, "last_name" : all_last_names, "team_name" : all_team_names, "odds" : all_odds})
    return results_df

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
            all_results_df = all_results_df.append(odds)

        for row_id, row in all_results_df.iterrows():
            player, created_player = Player.objects.get_or_create(first_name=row["first_name"], last_name=row["last_name"], team_name=row["team_name"])
            odds, created_odds = FanDuelOdds.objects.get_or_create(player=player, first_to_score_odds=row["odds"], date=date.today())
