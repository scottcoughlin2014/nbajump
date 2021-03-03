import requests
import pandas as pd
from pandas.io.json import json_normalize
from functools import reduce
from datetime import date
import datetime
import math

from pytz import timezone 
from django.core.management.base import BaseCommand, CommandError
from firsttoscore.models import Team, Game, Player

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
    projected_starters = []
    for k in jsonData["eventmarketgroups"][-1]["markets"]:
        if k["name"] == "Team to Score First":
            teams = []
            for idx, team_score_first_odds in enumerate(k["selections"]):
                all_team_names.append(team_score_first_odds["name"])
                game_odd = team_score_first_odds["currentpriceup"]/team_score_first_odds["currentpricedown"]
                if game_odd <1:
                    game_odd = (1/game_odd)*-100
                else:
                    game_odd = game_odd * 100
                all_odds.append(int(math.ceil(game_odd)))
        elif k["name"] == "First Basket":
            for idx, projected_game_starters in enumerate(k["selections"]):
                projected_starters.append(projected_game_starters["name"])

    try:
        results_df = pd.DataFrame({"away_team_name" : all_team_names[0], "a_odds" : all_odds[0], "home_team_name" : all_team_names[1], "h_odds" : all_odds[1], "projected_starters" : [projected_starters]}, index=[0])
    except:
        results_df = pd.DataFrame()
    return results_df

def clean_team_name(x):
    if x == "Los Angeles Clippers":
        return "LA Clippers"
    else:
        return x

def get_odds():
    jsonData_fanduel_nba = requests.get('https://sportsbook.fanduel.com/cache/psmg/US/55978.3.json').json()

    nba = parse_data(jsonData_fanduel_nba)

    all_results_df = pd.DataFrame()
    for gameid, hometeam, awayteam in zip(nba["idfoevent"], nba["participantname_home"], nba["participantname_away"]):
        jsonData_fanduel_nba = requests.get("https://sportsbook.fanduel.com/cache/psevent/US/1/false/{0}.json".format(gameid)).json()
        odds = parse_individual_game_data(jsonData_fanduel_nba, hometeam=hometeam, awayteam=awayteam)
        odds["gameid"] = gameid
        all_results_df = all_results_df.append(odds)

    all_results_df["home_team_name"] = all_results_df["home_team_name"].apply(clean_team_name)
    all_results_df["away_team_name"] = all_results_df["away_team_name"].apply(clean_team_name)

    for row_id, row in all_results_df.iterrows():
        h_team = Team.objects.get(full_name=row["home_team_name"])
        a_team = Team.objects.get(full_name=row["away_team_name"])
        # get the game info
        tz = timezone('EST')
        try:
            game = Game.objects.get(h_team=h_team.team_id, a_team=a_team.team_id, game_date=datetime.datetime.now(tz).strftime("%Y%m%d"))
        except:
            tomorrow_date = (datetime.datetime.now(tz) + datetime.timedelta(1)).strftime("%Y%m%d")
            game = Game.objects.get(h_team=h_team.team_id, a_team=a_team.team_id, game_date=tomorrow_date)
        game.h_odds = row["h_odds"]
        game.a_odds = row["a_odds"]
        game.fd_id = row["gameid"]
        # Find the nba player id assocaited with all the projected starters
        p_starter_ids = []
        for p_starter in row["projected_starters"]:
            p_starter_id = None
            if " Jr" in p_starter:
                p_starter = p_starter.replace(" Jr", " Jr.")
            if "." in p_starter.split(" ")[0]:
                p_starter = p_starter.replace(p_starter.split(" ")[0][-1] + ' ', p_starter.split(" ")[0][-1] + '. ')
            if p_starter == "Mo Wagner":
                p_starter = "Moritz Wagner"
            if p_starter == "Wendell Carter":
                p_starter = "Wendell Carter Jr."
            if p_starter == "Karl Anthony Towns":
                p_starter = "Karl-Anthony Towns"

            try:
                # See if last name is suff
                p_starter_id = Player.objects.get(team_id=a_team.team_id, first_name=' '.join(p_starter.split(" ")[0:-1]), last_name=p_starter.split(" ")[-1]).nba_id
            except:
                p_starter_id = Player.objects.get(team_id=h_team.team_id, first_name=' '.join(p_starter.split(" ")[0:-1]), last_name=p_starter.split(" ")[-1]).nba_id
            finally:
                if p_starter_id is None:
                    print("{0} not found".format(p_starter))
                    continue
            p_starter_ids.append(p_starter_id)
        if p_starter_ids:
            game.projected_starters = p_starter_ids
        game.save()

class Command(BaseCommand):
    help = 'Command to update or make new GRB for the bright.ciera.northwestern.edu webserver'

#    def add_arguments(self, parser):
#        parser.add_argument("--json-file", required=True)

    def handle(self, *args, **options):
        get_odds()
