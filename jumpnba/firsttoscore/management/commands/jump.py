#!/usr/bin/env python
from requests import get
from datetime import datetime,timedelta,date
from operator import itemgetter
import sys,json,os,argparse,pytz

from django.core.management.base import BaseCommand, CommandError
from players.models import Player
from firsttoscore.models import FanDuelOdds, FirstScorer

class Command(BaseCommand):
    help = 'Command to update or make new GRB for the bright.ciera.northwestern.edu webserver'

    def add_arguments(self, parser):
        parser.add_argument("--year",
                            help="Year for NBA data",
                            required=True, type=int)
        parser.add_argument("--tomorrow", help="Show tomorrow games instead of today's", default=0, action='store_true')

    def add_odds(self,player):
        try:
            player = Player.objects.get(first_name=players[team_stats[away_team]['first_scorer'][i][1]]["firstName"], last_name=players[team_stats[away_team]['first_scorer'][i][1]]["lastName"], team_name=teams[away_team]["fullName"])
            first_scorer, created = FirstScorer.objects.get_or_create(player=player)
            first_scorer.number_of_times = away_scorer[1]
            first_scorer.save()
            # get the latest odds for this player to score the first basket
            odds_away = FanDuelOdds.objects.filter(player=player, date=date.today()).last()
            away_first_to_score_odds = odds_away.first_to_score_odds
        except:
            away_first_to_score_odds = "N/A"
        away_first_to_score_odds_out= 'Odds {: >4}'.format(away_first_to_score_odds)

    def print_out(self,_field, _value1, _value2, _color):
        print('{: >35} {: >27} {: >27}'.format(_field,_color[0]+_value1,_color[1]+_value2))

    def printer(self,_line,color=['\033[00m','\033[00m'],percentage=0,player_list=0):
        value1=value2=''
        field=_line[0]
        
        #team stats printer
        if player_list==0:
            number1=_line[1]
            reference1=_line[2]
            value1= '{:>2}/{:>3}'.format(number1,reference1)
            if percentage==1 and reference1!=0:
                value1= value1 +' ({: >5.1f}%)\033[00m'.format(100.*number1/reference1)
            
            if len(_line)>3:
                number2=_line[3]
                reference2=_line[4]
                value2= '{:>2}/{:>3}'.format(number2,reference2)
                if percentage==1 and reference2!=0:
                    value2= value2 +' ({: >5.1f}%)\033[00m'.format(100.*number2/reference2)
    
            self.print_out(field, value1, value2, color)
        
        #player list printer
        else:
            pl_list1=_line[1]
            if len(_line)>2:
                pl_list2=_line[2]
        
            for i in range(len(pl_list1)):
                if len(pl_list1[i])==3:
                    value1='{: >17} {: >2}/{: >2}'.format(pl_list1[i][-1],pl_list1[i][0],pl_list1[i][1])
                else:
                    value1='{: >17} {: >2}'.format(pl_list1[i][-1],pl_list1[i][0])
                if len(_line)>2:
                    if len(pl_list2[i])==3:
                        value2='{: >17} {: >2}/{: >2}'.format(pl_list2[i][-1],pl_list2[i][0],pl_list2[i][1])
                    else:
                        value2='{: >17} {: >2}'.format(pl_list2[i][-1],pl_list2[i][0])

                if i==0:
                    self.print_out(field, value1, value2, color)
                else:
                    self.print_out('', value1, value2, color)



    def handle(self, *args, **options):
    
        class statistic:
            def __init__(self,_lab,_val,_ref,_badval,_goodval):
                self.field_label=_lab
                self.value=_val
                self.reference=_ref
                self.bad=_badval
                self.good=_goodval
                
        
        s_tip_off=statistic('tip-offs won','tip_off_won','game_played',.3,.7)
        s_scoring_tip_off=statistic('scored first after winning tip off','scored_first_after_winning_tip_off','tip_off_won',.2,.5)
        s_scored_first=statistic('scored first','scored_first','game_played',.3,.7)
        s_fouled_first=statistic('foul during first defence','foul_first_defence','game_played',.0,1.)
    
    
        tot_games=0
        tot_score_first_possession=0

        #_____________________________________________________________
        #get teams json. Download it once, and save it locally.
        #if the script doesn't find it, it will download it again
        team_json_file='teams.json'
        if not os.path.isfile(team_json_file):
            team_url = 'http://data.nba.net/prod/v1/{0}/teams.json'.format(options["year"])
            team_json=get(team_url).json()
            with open(team_json_file, 'w') as outfile:
                    json.dump(team_json, outfile, indent=4)

        t = open(team_json_file)
        teams = json.load(t)
        t.close()
        #reorganize the dictionary so that I can call all the info for
        #one team using its teamId
        teams={el['teamId']:el for el in teams["league"]["standard"]}

        team_stats={el:{'game_played':0,'tip_off_won':0,'scored_first_after_winning_tip_off':0,'missed_first_after_winning_tip_off':0,'scored_first':0,'foul_first_defence':0,'first_scorer':{},'first_shooter':{}} for el in teams}

        #_____________________________________________________________
        #get players json. Download it once, and save it locally.
        #if the script doesn't find it, it will download it again
        player_json_file='players_{0}.json'.format(options["year"])
        if not os.path.isfile(player_json_file):
            player_url = 'http://data.nba.net/prod/v1/{0}/players.json'.format(options["year"])
            player_json=get(player_url).json()
            with open(player_json_file, 'w') as outfile:
                    json.dump(player_json, outfile, indent=4)

        p = open(player_json_file)
        players = json.load(p)
        p.close()
        #reorganize the dictionary so that I can call all the info for
        #one player using his personId
        players={el['personId']:el for el in players["league"]["standard"]}



        #_____________________________________________________________
        #get the schedule json. Download it once, and save it locally.
        #if the script doesn't find it, it will download it again
        schedule_json_file='schedule_{0}.json'.format(options["year"])
        if not os.path.isfile(schedule_json_file):
            schedule_url = 'http://data.nba.net/prod/v2/{0}/schedule.json'.format(options["year"])
            schedule_json=get(schedule_url).json()
            with open(schedule_json_file, 'w') as outfile:
                json.dump(schedule_json, outfile, indent=4)

        s = open(schedule_json_file)
        schedule = json.load(s)
        s.close()
        #reorganize the dictionary so that I can call all the info for
        #one game using its gameId
        schedule={el['gameId']:el for el in schedule["league"]["standard"]}



        #checking what day is today to know what games have been played
        TODAY_UTC = datetime.utcnow()
        eastern = pytz.timezone('US/Eastern')
        TODAY = TODAY_UTC.astimezone(eastern)


        #scrolling through the games
        for gameId in schedule:
            game=schedule[gameId]
            #getting time of the game, in UTC
            game_time=datetime.strptime(game["startTimeUTC"], '%Y-%m-%dT%H:%M:%S.%fZ')
            
            #___________________________________________
            # game["seasonStageId"]==1 -> pre-season
            # game["seasonStageId"]==2 -> regular-season
            # game["seasonStageId"]==3 -> exhibition game (like the All-Star Game)
            # game["seasonStageId"]==4 -> playoffs
            #___________________________________________
            
            # skipping games not played yet, and including only main-season.
            if (game_time > TODAY_UTC) or game["seasonStageId"]==1 or game["seasonStageId"]==3:
                continue

            #keep track of the total number of games played
            tot_games+=1

            #this is just the day of the game in Eastern time.
            #you need this to fetch the play-by-play
            gameDate=game["startDateEastern"]

            #keeping track of which teams are playing
            home_team=game["hTeam"]["teamId"]
            team_stats[home_team]['game_played']+=1

            away_team=game["vTeam"]["teamId"]
            team_stats[away_team]['game_played']+=1
    
            #_____________________________________________________________
            #fetching the play-by-play of the first period of the game
            #the number '1' at the end of the url refer to the period
            #if you want more than the first period, change that

            #Download the json once, and save it locally.
            #if the script doesn't find it, it will download it again
            season_dir='{0}_season'.format(options["year"])
            if not os.path.isdir(season_dir):
                os.system('mkdir {0}'.format(season_dir))
            pbp_json_file='{0}/{1}.json'.format(season_dir,gameId)
            if not os.path.isfile(pbp_json_file):
                pbp_url='http://data.nba.net/prod/v1/{0}/{1}_pbp_1.json'.format(gameDate,gameId)
                pbp_json=get(pbp_url).json()
                with open(pbp_json_file, 'w') as outfile:
                    json.dump(pbp_json, outfile, indent=4)

            p = open(pbp_json_file)
            json_pbp = json.load(p)
            p.close()

            #I found a json with no plays. Perhaps a postponed game? Need to investigate.
            if len(json_pbp["plays"])==0:
                continue

            #First play (i.e. [0]) is always the start.
            #Second is always the tip-off.
            #I keep track of the first 2 plays after the tip-off
            for i,play in enumerate(json_pbp["plays"]):
                if play["eventMsgType"]=="10":
                    tip_off=json_pbp["plays"][i]
                    play_1=json_pbp["plays"][i+1]
                    play_2=json_pbp["plays"][i+2]
                    break

            #recording who won the tip-off, and what team got possesion.
            tip_off_winner_p=tip_off["personId"]
            team_stats[tip_off["teamId"]]['tip_off_won']+=1

            #I can use the "eventMsgType" argument to know what happened
            #___________________________________________
            #play["eventMsgType"]==1 -> shot made
            #play["eventMsgType"]==2 -> shot missed
            #play["eventMsgType"]==3 -> free throw
            #play["eventMsgType"]==4 -> rebound
            #play["eventMsgType"]==5 -> turnover
            #play["eventMsgType"]==6 -> foul
            #play["eventMsgType"]==10 -> Jump ball
            #play["eventMsgType"]==12 -> Start period
            #play["eventMsgType"]==20 -> Stoppage: Out-of-Bounds
            #___________________________________________


            #first possession resulted in scoring if the first was a scored shot
            #or the first play was a foul and the second was a scored free throw
            #need to check how missed free throw are recorded
            if play_1["eventMsgType"]=="1" or play_2["eventMsgType"]=="3":
                team_stats[tip_off["teamId"]]['scored_first_after_winning_tip_off']+=1
                #marking that who won the tip-off also scored first
                tot_score_first_possession+=1
            else:
                #this is very likely superfluous
                team_stats[tip_off["teamId"]]['missed_first_after_winning_tip_off']+=1

            #keeping track also if teams tend to make fouls during the first play
            if play_1["eventMsgType"]=="6":
                team_stats[play_1["teamId"]]['foul_first_defence']+=1



            #________________________________________________________
            #now I want to check who scored first for each team
            #"isScoreChange" record a a change in the score.
            #So I can use that to know when somebody scored.

            #switch to check if someone already scored
            score=0
            shot=0

            #looking at all plays after the tip-off
            for play in json_pbp["plays"][2:]:
                if play["personId"]=='':
                    continue
                
                #first shooter
                if shot==0 and play["eventMsgType"] in ["1","2","3"]:
                    shooter=play["personId"]
                    #adding the shooter to the teams list of first shooter.
                    if shooter not in team_stats[play["teamId"]]['first_shooter']:
                        team_stats[play["teamId"]]['first_shooter'][shooter]=[0,0]
                    team_stats[play["teamId"]]['first_shooter'][shooter][1]+=1
                    if play["isScoreChange"]==1:
                        team_stats[play["teamId"]]['first_shooter'][shooter][0]+=1
                    #tracking what team scored already
                    #and change the switch that somebody scored
                    shooting_team=play["teamId"]
                    shot=1
                
                if shot==1 and play["eventMsgType"] in ["1","2","3"] and play["teamId"]!= shooting_team:
                    shooter=play["personId"]
                    #adding the shooter to the teams list of first shooter.
                    if shooter not in team_stats[play["teamId"]]['first_shooter']:
                        team_stats[play["teamId"]]['first_shooter'][shooter]=[0,0]
                    team_stats[play["teamId"]]['first_shooter'][shooter][1]+=1
                    if play["isScoreChange"]==1:
                        team_stats[play["teamId"]]['first_shooter'][shooter][0]+=1
                    shot=2
            
                #first team score
                if score==0 and play["isScoreChange"]==1:
                    team_stats[play["teamId"]]['scored_first']+=1
                    scorer=play["personId"]
                    #adding the scorer to the teams list of first scorers.
                    if scorer not in team_stats[play["teamId"]]['first_scorer']:
                        team_stats[play["teamId"]]['first_scorer'][scorer]=0
                    team_stats[play["teamId"]]['first_scorer'][scorer]+=1
                    #tracking what team scored already
                    #and change the switch that somebody scored
                    scoring_team=play["teamId"]
                    score=1
            
                #second team scored, if somebody scored
                #and the team is not the one which scored already
                if score==1 and play["isScoreChange"]==1 and play["teamId"]!= scoring_team:
                    scorer=play["personId"]
                    if scorer not in team_stats[play["teamId"]]['first_scorer']:
                        team_stats[play["teamId"]]['first_scorer'][scorer]=0
                    team_stats[play["teamId"]]['first_scorer'][scorer]+=1
                    #both team scored, so I con exit the loop
                    break


        #sort first scorers
        #note that I'm changeing team_stats[_team]['first_scorer']
        #from dictionary to list
        for _team in team_stats:
            tmp_list=[]
            for el in team_stats[_team]['first_scorer']:
                try:
                    last_name=players[el]["lastName"]
                except:
                    last_name='??'
                tmp_list.append([team_stats[_team]['first_scorer'][el],last_name])
            team_stats[_team]['first_scorer'] = sorted(tmp_list, reverse=True)
            
            tmp_list=[]
            for el in team_stats[_team]['first_shooter']:
                try:
                    last_name=players[el]["lastName"]
                except:
                    last_name='??'
                tmp_list.append([team_stats[_team]['first_shooter'][el][0],team_stats[_team]['first_shooter'][el][1],last_name])
            team_stats[_team]['first_shooter'] = sorted(tmp_list, reverse=True,key=itemgetter(1,0))
            



        #End of collecting data
        #########

        #just printing out what the script learnt for all the teams.
        print("---All teams---")
        for _team in team_stats:
            print('['+teams[_team]["fullName"]+']')
            print("_"*63)
			
   
            #looping through the statistic field we consider
            for stat in [s_tip_off,s_scoring_tip_off,s_scored_first,s_fouled_first]:
                #start list for output
                out_stats=[stat.field_label,team_stats[_team][stat.value],team_stats[_team][stat.reference]]
                self.printer(out_stats,percentage=1)

            for stat in ['first_shooter','first_scorer']:
                print(' - '*21)
                self.printer([stat,team_stats[_team][stat]],player_list=1)


            print('\n\n')

        print('Times that winning the tip-off resulted in the team scoring first:')
        print(tot_score_first_possession,'/',tot_games,' (','%.1f'%(100.*tot_score_first_possession/tot_games),'%)',sep='')


        print('\n\n')



        #Checking what games are played today
        if options["tomorrow"]:
            date_to_show="|"+" "*47+"TOMORROW'S GAMES"+" "*48+"|"
            TOMORROW = TODAY + timedelta(days=1)
            date_check=TOMORROW.strftime("%Y%m%d")
        else:
            date_to_show="|"+" "*49+"TODAY'S GAMES"+" "*49+"|"
            date_check=TODAY.strftime("%Y%m%d")

        print("_"*113)
        print("|"+" "*111+"|")
        print(date_to_show)
        print("|"+" "*111+"|")
        print("_"*113)
        game_counter=0
        for gameId in schedule:
            game=schedule[gameId]
            if game["startDateEastern"]==date_check:
                game_counter+=1
                game_time='GAME %d - %s (Eastern time)'%(game_counter,game["startTimeEastern"])
                home_team=game["hTeam"]["teamId"]
                away_team=game["vTeam"]["teamId"]
                print('\n')
                print('{: >35} {: >38} {: >38}'.format(game_time,'['+teams[away_team]["fullName"]+']', '['+teams[home_team]["fullName"]+']'))
                print("_"*113)
                
                playing_teams=[away_team,home_team]
                
                #Printing team statistics for specific matchup
                #looping through the statistic field we consider
                for stat in [s_tip_off,s_scoring_tip_off,s_scored_first,s_fouled_first]:
                    #start list for output
                    out_stats=[stat.field_label]
                    
                    #start with neutral color
                    color=['\033[00m','\033[00m']
                    
                    for i,_team in enumerate(playing_teams):
                        #This is the conditions for a bad statistic -> red color
                        if team_stats[_team][stat.value]/team_stats[_team][stat.reference]<stat.bad:
                            color[i]='\033[41m' #red
                        #This is the conditions for a bad statistic -> green color
                        elif team_stats[_team][stat.value]/team_stats[_team][stat.reference]>=stat.good:
                            color[i]='\033[42m' #green
                        
                        #expanding the output list with the correct values for away/home team
                        out_stats.extend([team_stats[_team][stat.value],team_stats[_team][stat.reference]])
                    
                    #printing out
                    self.printer(out_stats,color,percentage=1)
            


                print(' '*21+' - '*31)
                
                for stat in ['first_shooter']:#,'first_scorer']:
                    out_stats=[stat]
                    
                    n_players=[]
                    
                    #store how many players are in the list for each team.
                    for i,_team in enumerate(playing_teams):
                        n_players.append(len(team_stats[_team][stat]))
                    
                    #check if list of players is differnt length between home and away team.
                    if n_players[0]!=n_players[1]:
                        dif=max(n_players)-min(n_players)
                        #getting which team has less players in their list
                        less=playing_teams[n_players.index(min(n_players))]
        
                        #Adding a blank line to team with less players, for display purposes
                        team_stats[less][stat].extend([['']*len(team_stats[less][stat][0])]*dif)
                        #team_stats[less][stat]=team_stats[less][stat][:n_players[idx_more]]
                    
                    for i,_team in enumerate(playing_teams):
                        out_stats.extend([team_stats[_team][stat]])
                
                    self.printer(out_stats,player_list=1)

#                for i in range(max(n_players)):
#                    if team_stats[away_team]['first_shooter'][i]=='':
#                        away_shooter= ['','',' ','']
#                        away_first_to_score_odds_out= ''
#                    else:
#                        away_shooter= [team_stats[away_team]['first_shooter'][i][2],team_stats[away_team]['first_shooter'][i][0],'/',team_stats[away_team]['first_shooter'][i][1]]
#                        try:
#                            player = Player.objects.get(first_name=players[team_stats[away_team]['first_shooter'][i][2]]["firstName"], last_name=team_stats[away_team]['first_shooter'][i][2], team_name=teams[away_team]["fullName"])
#                            first_scorer, created = FirstScorer.objects.get_or_create(player=player)
#                            first_scorer.number_of_times = away_scorer[1]
#                            first_scorer.save()
#                            # get the latest odds for this player to score the first basket
#                            odds_away = FanDuelOdds.objects.filter(player=player, date=date.today()).last()
#                            away_first_to_score_odds = odds_away.first_to_score_odds
#                        except:
#                            away_first_to_score_odds = "N/A"
#                        away_first_to_score_odds_out= 'Odds {: >4}'.format(away_first_to_score_odds)
#
#                    if team_stats[home_team]['first_shooter'][i]=='':
#                        home_shooter= ['','',' ','']
#                        home_first_to_score_odds_out= ''
#                    else:
#                        home_shooter= [team_stats[home_team]['first_shooter'][i][2],team_stats[home_team]['first_shooter'][i][0],'/',team_stats[home_team]['first_shooter'][i][1]]
#                        try:
#                            player = Player.objects.get(first_name=players[team_stats[home_team]['first_shooter'][i][2]]["firstName"], last_name=team_stats[home_team]['first_shooter'][i][2], team_name=teams[home_team]["fullName"])
#                            first_scorer, created = FirstScorer.objects.get_or_create(player=player)
#                            first_scorer.number_of_times = home_scorer[1]
#                            first_scorer.save()
#                            # get the latest odds for this player to score the first basket
#                            odds_home = FanDuelOdds.objects.filter(player=player, date=date.today()).last()
#                            home_first_to_score_odds = odds_home.first_to_score_odds
#                        except:
#                            home_first_to_score_odds = "N/A"
#                        home_first_to_score_odds_out= 'Odds {: >4}'.format(home_first_to_score_odds)
#
#
#                    if i==0:
#                        print('{: >35} {: >18} {: >2}{}{: >2}  {: >10} {: >18} {: >2}{}{: >2}  {: >10}'.format('First shooters:', away_shooter[0],away_shooter[1],away_shooter[2],away_shooter[3],away_first_to_score_odds_out,home_shooter[0],home_shooter[1],home_shooter[2],home_shooter[3],home_first_to_score_odds_out))
#                    else:
#                        print('{: >35} {: >18} {: >2}{}{: >2}  {: >10} {: >18} {: >2}{}{: >2}  {: >10}'.format('', away_shooter[0],away_shooter[1],away_shooter[2],away_shooter[3],away_first_to_score_odds_out,home_shooter[0],home_shooter[1],home_shooter[2],home_shooter[3],home_first_to_score_odds_out))

                print(' '*21+' - '*31)
                
                
                
                
                away_n_scorers=len(team_stats[away_team]['first_scorer'])
                home_n_scorers=len(team_stats[home_team]['first_scorer'])
                
                if away_n_scorers>home_n_scorers:
                    team_stats[home_team]['first_scorer'].extend(['','']*away_n_scorers)
                    team_stats[home_team]['first_scorer']=team_stats[home_team]['first_scorer'][:away_n_scorers]
                elif home_n_scorers>away_n_scorers:
                    team_stats[away_team]['first_scorer'].extend(['','']*home_n_scorers)
                    team_stats[away_team]['first_scorer']=team_stats[away_team]['first_scorer'][:home_n_scorers]

                
                for i in range(max([away_n_scorers,home_n_scorers])):
                    if team_stats[away_team]['first_scorer'][i]=='':
                        away_scorer= ['','']
                        away_first_to_score_odds_out=''
                    else:
                        away_scorer=[team_stats[away_team]['first_scorer'][i][1],team_stats[away_team]['first_scorer'][i][0]]
                        try:
                            player = Player.objects.get(first_name=players[team_stats[away_team]['first_scorer'][i][1]]["firstName"], last_name=players[team_stats[away_team]['first_scorer'][i][1]]["lastName"], team_name=teams[away_team]["fullName"])
                            first_scorer, created = FirstScorer.objects.get_or_create(player=player)
                            first_scorer.number_of_times = away_scorer[1]
                            first_scorer.save()
                            # get the latest odds for this player to score the first basket
                            odds_away = FanDuelOdds.objects.filter(player=player, date=date.today()).last()
                            away_first_to_score_odds = odds_away.first_to_score_odds
                        except:
                            away_first_to_score_odds = "N/A"
                        away_first_to_score_odds_out= 'Odds {: >4}'.format(away_first_to_score_odds)

                    if team_stats[home_team]['first_scorer'][i]=='':
                        home_scorer= ['','']
                        home_first_to_score_odds_out=''
                    else:
                        home_scorer= [team_stats[home_team]['first_scorer'][i][1],team_stats[home_team]['first_scorer'][i][0]]
                        try:
                            player = Player.objects.get(first_name=players[team_stats[home_team]['first_scorer'][i][1]]["firstName"], last_name=team_stats[home_team]['first_scorer'][i][1], team_name=teams[home_team]["fullName"])
                            first_scorer, created = FirstScorer.objects.get_or_create(player=player)
                            first_scorer.number_of_times = home_scorer[1]
                            first_scorer.save()
                            # get the latest odds for this player to score the first basket
                            odds_home = FanDuelOdds.objects.filter(player=player, date=date.today()).last()
                            home_first_to_score_odds = odds_home.first_to_score_odds
                        except:
                            home_first_to_score_odds = "N/A"
                        home_first_to_score_odds_out= 'Odds {: >4}'.format(home_first_to_score_odds)

                    if i==0:
                        print('{: >35} {: >21} {: >2}  {: >10} {: >21} {: >2}  {: >10}'.format('First scorers:',away_scorer[0],away_scorer[1],away_first_to_score_odds_out,home_scorer[0],home_scorer[1], home_first_to_score_odds_out))
                    else:
                        print('{: >35} {: >21} {: >2}  {: >10} {: >21} {: >2}  {: >10}'.format('', away_scorer[0],away_scorer[1],away_first_to_score_odds_out,home_scorer[0],home_scorer[1], home_first_to_score_odds_out))


                print('\n')
