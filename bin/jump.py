#!/usr/bin/env python
from requests import get
from datetime import datetime
import sys,json,os,argparse

def parse_commandline():
    """Parse the arguments given on the command-line.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year",
                        help="Year for NBA data",
                        required=True, type=int)
    args = parser.parse_args()

    return args

# READ COMMANDLINE ARGUMENTS
###########################################################################
args = parse_commandline()

tot_games=0
tot_score_first_possession=0

#_____________________________________________________________
#get teams json. Download it once, and save it locally.
#if the script doesn't find it, it will download it again
if not os.path.isfile('teams.json'):
    team_url = 'http://data.nba.net/prod/v1/{0}/teams.json'.format(args.year)
    team_json=get(team_url).json()
    with open('teams.json', 'w') as outfile:
            json.dump(team_json, outfile, indent=4)

t = open('teams.json')
teams = json.load(t)
t.close()
#reorganize the dictionary so that I can call all the info for
#one team using its teamId
teams={el['teamId']:el for el in teams["league"]["standard"]}

team_stats={el:{'game_played':0,'tip_off_won':0,'scored_first_after_winning_tip_off':0,'missed_first_after_winning_tip_off':0,'scored_first':0,'foul_first_defence':0,'first_scorer':{}} for el in teams}

#_____________________________________________________________
#get players json. Download it once, and save it locally.
#if the script doesn't find it, it will download it again
if not os.path.isfile('players_2020.json'):
    player_url = 'http://data.nba.net/prod/v1/2020/players.json'
    player_json=get(player_url).json()
    with open('players_2020.json', 'w') as outfile:
            json.dump(player_json, outfile, indent=4)

p = open('players_2020.json')
players = json.load(p)
p.close()
#reorganize the dictionary so that I can call all the info for
#one player using his personId
players={el['personId']:el for el in players["league"]["standard"]}



#_____________________________________________________________
#get the schedule json. Download it once, and save it locally.
#if the script doesn't find it, it will download it again
if not os.path.isfile('schedule_2020.json'):
    schedule_url = 'http://data.nba.net/prod/v2/2020/schedule.json'
    schedule_json=get(schedule_url).json()
    with open('schedule_2020.json', 'w') as outfile:
        json.dump(schedule_json, outfile, indent=4)

s = open('schedule_2020.json')
schedule = json.load(s)
s.close()
#reorganize the dictionary so that I can call all the info for
#one game using its gameId
schedule={el['gameId']:el for el in schedule["league"]["standard"]}



#checking what day is today to know what games have been played
TODAY = datetime.today()
TODAY_UTC = datetime.utcnow()


#scrolling through the games
for gameId in schedule:
    game=schedule[gameId]
    #getting time of the game, in UTC
    game_time=datetime.strptime(game["startTimeUTC"], '%Y-%m-%dT%H:%M:%S.%fZ')
    
    #___________________________________________
    # game["seasonStageId"]==1 -> Pre-season
    # game["seasonStageId"]==2 -> Main-season
    #___________________________________________
    
    # skipping games not played yet, and including only main-season.
    if (game_time > TODAY_UTC) or game["seasonStageId"]!=2:
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
    if not os.path.isdir('2020_season'):
        os.system('mkdir 2020_season')
    if not os.path.isfile('2020_season/'+gameId+'.json'):
        pbp_url='http://data.nba.net/prod/v1/'+gameDate+'/'+gameId+'_pbp_1.json'
        pbp_json=get(pbp_url).json()
        with open('2020_season/'+gameId+'.json', 'w') as outfile:
            json.dump(pbp_json, outfile, indent=4)

    p = open('2020_season/'+gameId+'.json')
    json_pbp = json.load(p)
    p.close()

    #I found a json with no plays. Perhaps a postponed game? Need to investigate.
    if len(json_pbp["plays"])==0:
        continue

    #First play (i.e. [0]) is always the start.
    #Second is always the tip-off.
    #I keep track of the first 2 plays after the tip-off
    tip_off=json_pbp["plays"][1]
    play_1=json_pbp["plays"][2]
    play_2=json_pbp["plays"][3]

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

    #looking at all plays after the tip-off
    for play in json_pbp["plays"][2:]:
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
    team_stats[_team]['first_scorer'] = sorted([[team_stats[_team]['first_scorer'][el],el] for el in team_stats[_team]['first_scorer']], reverse=True)


#End of collecting data
#########




#just printin out what the script learnt for all the teams.
print("---All teams---")
for _team in team_stats:
    print('['+teams[_team]["fullName"]+']')
    print("_"*61)
    
    tip_off= '%d/%d (%.1f%%)' %(team_stats[_team]['tip_off_won'],team_stats[_team]['game_played'],100.*team_stats[_team]['tip_off_won']/team_stats[_team]['game_played'])
    print('{: >35} {: >25}'.format('tip-offs won:',tip_off))
    
    
    if team_stats[_team]['tip_off_won'] !=0:
            scored_after_tip_off= '%d/%d (%.1f%%)' %(team_stats[_team]['scored_first_after_winning_tip_off'],team_stats[_team]['tip_off_won'],100.*team_stats[_team]['scored_first_after_winning_tip_off']/team_stats[_team]['tip_off_won'])
    else:
            scored_after_tip_off= '%d/%d' %(team_stats[_team]['scored_first_after_winning_tip_off'],team_stats[_team]['tip_off_won'])
    print('{: >35} {: >25}'.format('scored after winning the tip-off:',scored_after_tip_off))


    scored_first= '%d/%d (%.1f%%)' %(team_stats[_team]['scored_first'],team_stats[_team]['game_played'],100.*team_stats[_team]['scored_first']/team_stats[_team]['game_played'])
    print('{: >35} {: >25}'.format('scored first:',scored_first))


    foul_first= '%d/%d (%.1f%%)' %(team_stats[_team]['foul_first_defence'],team_stats[_team]['game_played'],100.*team_stats[_team]['foul_first_defence']/team_stats[_team]['game_played'])
    print('{: >35} {: >25}'.format('foul during first defence:',foul_first))
            


    for i in range(len(team_stats[_team]['first_scorer'])):
        scorer= [players[team_stats[_team]['first_scorer'][i][1]]["lastName"],team_stats[_team]['first_scorer'][i][0]]
        if i==0:
            print('{: >35} {: >21} {: >3}'.format('First scorers:',scorer[0],scorer[1]))
        else:
            print('{: >35} {: >21} {: >3}'.format('',scorer[0],scorer[1]))
                            
                            
    print("\nFirst scorers:")
#	for _player in team_stats[_team]['first_scorer']:
#		print('-'+ players[_player]["lastName"]+' '+str(team_stats[_team]['first_scorer'][_player]))
    print('\n\n')

print('Times that winning the tip-off resulted in the team scoring first:')
print(tot_score_first_possession,'/',tot_games,' (','%.1f'%(100.*tot_score_first_possession/tot_games),'%)',sep='')


print('\n\n')

#Checking what games are played today
print("_"*87)
print("|"+" "*85+"|")
print("|"+" "*36+"TODAY'S GAMES"+" "*36+"|")
print("|"+" "*85+"|")
print("_"*87)
game_counter=0
for gameId in schedule:
    game=schedule[gameId]
    if game["startDateEastern"]==TODAY.strftime("%Y%m%d"):
        game_counter+=1
        game_time='GAME %d - %s (Eastern time)'%(game_counter,game["startTimeEastern"])
        home_team=game["hTeam"]["teamId"]
        away_team=game["vTeam"]["teamId"]
        print('\n')
        print('{: >35} {: >25} {: >25}'.format(game_time,'['+teams[away_team]["fullName"]+']', '['+teams[home_team]["fullName"]+']'))
        print("_"*87)
        
        away_tip_off= '%d/%d (%.1f%%)' %(team_stats[away_team]['tip_off_won'],team_stats[away_team]['game_played'],100.*team_stats[away_team]['tip_off_won']/team_stats[away_team]['game_played'])
        home_tip_off= '%d/%d (%.1f%%)' %(team_stats[home_team]['tip_off_won'],team_stats[home_team]['game_played'],100.*team_stats[home_team]['tip_off_won']/team_stats[home_team]['game_played'])
        print('{: >35} {: >25} {: >25}'.format('tip-offs won:',away_tip_off,home_tip_off))
        
        
        if team_stats[away_team]['tip_off_won']!=0:
            away_scored_after_tip_off= '%d/%d (%.1f%%)' %(team_stats[away_team]['scored_first_after_winning_tip_off'],team_stats[away_team]['tip_off_won'],100.*team_stats[away_team]['scored_first_after_winning_tip_off']/team_stats[away_team]['tip_off_won'])
        else:
            away_scored_after_tip_off= '%d/%d' %(team_stats[away_team]['scored_first_after_winning_tip_off'],team_stats[away_team]['tip_off_won'])
        
        if team_stats[home_team]['tip_off_won']!=0:
            home_scored_after_tip_off= '%d/%d (%.1f%%)' %(team_stats[home_team]['scored_first_after_winning_tip_off'],team_stats[home_team]['tip_off_won'],100.*team_stats[home_team]['scored_first_after_winning_tip_off']/team_stats[home_team]['tip_off_won'])
        else:
            home_scored_after_tip_off= '%d/%d' %(team_stats[home_team]['scored_first_after_winning_tip_off'],team_stats[home_team]['tip_off_won'])
        print('{: >35} {: >25} {: >25}'.format('scored after winning the tip-off:',away_scored_after_tip_off,home_scored_after_tip_off))
        

        away_scored_first= '%d/%d (%.1f%%)' %(team_stats[away_team]['scored_first'],team_stats[away_team]['game_played'],100.*team_stats[away_team]['scored_first']/team_stats[away_team]['game_played'])
        home_scored_first= '%d/%d (%.1f%%)' %(team_stats[home_team]['scored_first'],team_stats[home_team]['game_played'],100.*team_stats[home_team]['scored_first']/team_stats[home_team]['game_played'])
        print('{: >35} {: >25} {: >25}'.format('scored first:',away_scored_first,home_scored_first))


        away_foul_first= '%d/%d (%.1f%%)' %(team_stats[away_team]['foul_first_defence'],team_stats[away_team]['game_played'],100.*team_stats[away_team]['foul_first_defence']/team_stats[away_team]['game_played'])
        home_foul_first= '%d/%d (%.1f%%)' %(team_stats[home_team]['foul_first_defence'],team_stats[home_team]['game_played'],100.*team_stats[home_team]['foul_first_defence']/team_stats[home_team]['game_played'])
        print('{: >35} {: >25} {: >25}'.format('foul during first defence:',away_foul_first,home_foul_first))
        
        away_n_scorers=len(team_stats[away_team]['first_scorer'])
        home_n_scorers=len(team_stats[home_team]['first_scorer'])
        
        if away_n_scorers>home_n_scorers:
            team_stats[home_team]['first_scorer'].extend(['','']*away_n_scorers)
            team_stats[home_team]['first_scorer']=team_stats[home_team]['first_scorer'][:away_n_scorers]
        elif home_n_scorers>away_n_scorers:
            team_stats[away_team]['first_scorer'].extend(['','']*home_n_scorers)
            team_stats[away_team]['first_scorer']=team_stats[away_team]['first_scorer'][:home_n_scorers]

        
        for i in range(max([away_n_scorers,home_n_scorers])):
            away_scorer= ['',''] if team_stats[away_team]['first_scorer'][i]=='' else [players[team_stats[away_team]['first_scorer'][i][1]]["lastName"],team_stats[away_team]['first_scorer'][i][0]]
            home_scorer= ['',''] if team_stats[home_team]['first_scorer'][i]=='' else [players[team_stats[home_team]['first_scorer'][i][1]]["lastName"],team_stats[home_team]['first_scorer'][i][0]]
            if i==0:
                print('{: >35} {: >21} {: >3} {: >21} {: >3}'.format('First scorers:',away_scorer[0],away_scorer[1],home_scorer[0],home_scorer[1]))
            else:
                print('{: >35} {: >21} {: >3} {: >21} {: >3}'.format('',away_scorer[0],away_scorer[1],home_scorer[0],home_scorer[1]))


        print('\n')
