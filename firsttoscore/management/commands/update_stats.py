#!/usr/bin/env python
from requests import get
import json,argparse,sys
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from firsttoscore.models import Player
from firsttoscore.models import Team
from firsttoscore.models import Game

def compareRating(_player_elo, _opponent_elo):
    """
    Compares the two ratings of the this player and the opponent.
    @param opponent - the player to compare against.
    @returns - The expected score between the two players.
    """
    return ( 1+10**( ( _opponent_elo-_player_elo )/400.0 ) ) ** -1

def updateELO(_id1, _id2, _winner_id):

    player1 = Player.objects.get(nba_id=_id1)
    player2 = Player.objects.get(nba_id=_id2)
    
    rating1 = player1.elo_score
    rating2 = player2.elo_score

    expected1 = compareRating(rating1,rating2)
    expected2 = compareRating(rating2,rating1)

    if _winner_id == _id1:
        score1 = 1.0
        score2 = 0.0
    elif _winner_id == _id2:
        score1 = 0.0
        score2 = 1.0

    #20 jumps are the minimum for the elo_score to be considered reliable
    if player1.jumps_jumped <= 20:
        k_factor_1 = 40
    else:
        k_factor_1 = 20

    if player2.jumps_jumped <= 20:
        k_factor_2 = 40
    else:
        k_factor_2 = 20


    newRating1 = rating1 + k_factor_1 * (score1 - expected1)
    newRating2 = rating2 + k_factor_2 * (score2 - expected2)

    if newRating1 < 0:
        newRating1 = 0
        newRating2 = rating2 - rating1

    elif newRating2 < 0:
        newRating2 = 0
        newRating1 = rating1 - rating2

    player1.elo_score = newRating1
    player2.elo_score = newRating2
    
    player1.save()
    player2.save()
    
    return newRating1,newRating2

def find_starters(pbp,_year):
    starters={}
    exclude=[]
    n_start=0
    
    #search along the plays what teams and what players are mentioned.
    for p in pbp["plays"]:
        skip=0
        if p["eventMsgType"]=="10":continue
        if "teamId" in p:
            if p["teamId"]=='':continue
            if p["teamId"] not in starters:
                starters[p["teamId"]]=[]
        if "personId" in p:
            if (p["personId"] not in starters[p["teamId"]]) and (p["personId"]!=p["teamId"]) and (p["personId"]!='') and (int(p["personId"]) not in exclude) and (Player.objects.filter(nba_id = p["personId"]).exists()):
                starters[p["teamId"]].append(p["personId"])
                n_start+=1
        
        #tracking players who enter late, and adding them to the exclude list
        if p["eventMsgType"]=="8":

            team_sub=p["teamId"]
    
            sub_in=p["description"].split(' by ')[1]
            players=Player.objects.filter(last_name=sub_in)
            
            #if it finds 0 players, the scrapping failed, so refines the name search.

            while 1:
                if len(players)!=0:
                    break
                elif len(sub_in)==0:
                    skip=1
                    break
                else:
                    sub_in=' '.join(sub_in.split()[1:])
                    players=Player.objects.filter(last_name=sub_in)
        
            if skip:
                continue
            if len(players)==1:
                exclude.append(players[0].nba_id)
            else:
                #if there are moree players with the same name, checks who was playing in that team in that year
                for _p in players:
                    for _t in _p.prev_teams:
                        if (team_sub == _t["teamId"]) and int(_t["seasonStart"])<=int(_year) and int(_t["seasonEnd"])>=int(_year):
                            exclude.append(_p.nba_id)
                            break
        
        if n_start==10:
            break
    
    for _t in starters:
        starters[_t]=[int(el) for el in starters[_t]]
    
    return starters

def most_probable_jumper(_starters):
    jumpers=[]
    for _p in _starters:
        players=Player.objects.get(nba_id=_p)
        if players.is_jumper==1:
            jumpers.append([players.jumps_jumped,players.nba_id])
    return int(sorted(jumpers,reverse=1)[0][1])



def find_jumpers(jump_play,_starters,_year):
    
    try:
        j=jump_play["description"].split(' vs ')
        j1=' '.join(j[0].split()[2:])
        j2=j[1].split(' (')[0]
    except:
        j=jump_play["description"].split(' \u8207 ')
        j1=j[0]
        j2=j[1].split('  \u8df3')[0]

    jumpers={_t:[] for _t in _starters}
    
    if j1==j2:
        for _t in _starters:
            for _p in _starters[_t]:
                s=Player.objects.get(nba_id=_p).last_name
                if s==j1:
                    jumpers[_t].append(_p)
                    team_found=_t
                    break
        
        if sum([len(jumpers[_t]) for _t in jumpers])!=2:
            for _t in _starters:
                if _t!=team_found:
                    team_to_be_found=_t
                    break

            jumpers[team_to_be_found].append(most_probable_jumper(_starters[team_to_be_found]))


    else:
        remaining=[]
        for _j in [j1,j2]:
            players=Player.objects.filter(last_name=_j)
            if len(players)==0:
                for _t_j in _j.split():
                    players=Player.objects.filter(last_name=_t_j)
                    if len(players)!=0:
                        break
        
            if len(players)==1:
                team_found=0
                for _t in _starters:
                    if players[0].nba_id in _starters[_t]:
                        jumpers[_t].append(players[0].nba_id)
                        team_found=1
                if not team_found:
                    for _t in _starters:
                        if players[0].nba_id in Team.objects.get(team_id=_t).stats[_year]['jumper_list']:
                            jumpers[_t].append(players[0].nba_id)
        
            
            else:
                remaining.append(players)
        
        remaining_team=[]
        for _t in jumpers:
            if len(jumpers[_t])==0:
                remaining_team.append(_t)

        for _j in remaining:
            team_found=0
            for pl in _j:
                for _t in remaining_team:
                    if pl.nba_id in _starters[_t]:
                        jumpers[_t].append(pl.nba_id)
                        team_found=1

            if not team_found:
                for pl in _j:
                    for _t in remaining_team:
                        if pl.nba_id in Team.objects.get(team_id=_t).stats[_year]['jumper_list']:
                            jumpers[_t].append(pl.nba_id)

        for _t in _starters:
            if len(jumpers[_t])>1:
                final=[]
                for _j in jumpers[_t]:
                    j=Player.objects.get(nba_id=_j)
                    if j.is_jumper==1:
                        final.append(_j)

                jumpers[_t]=final[:]

    #ret_jump=[]
    for _t in jumpers:
        if len(jumpers[_t])!=1:
            print(_t,jumpers)
            sys.exit()
    #    ret_jump.append(int(jumpers[_t][0]))
    jumpers={_t:[int(jumpers[_t][0])] for _t in jumpers}

    return jumpers

def update_stats(_year):
    #_____________________________________________________________
    #get the schedule json. Download it once, and save it locally.
    #if the script doesn't find it, it will download it again
    year=str(_year)

    #checking what day is today to know what games have been played
    TODAY_UTC = timezone.now()

    schedule=Game.objects.filter(season=year)

    #scrolling through the games
    for game in schedule:
    
        #___________________________________________
        # game["seasonStageId"]==1 -> pre-season
        # game["seasonStageId"]==2 -> regular-season
        # game["seasonStageId"]==3 -> exhibition game (like the All-Star Game)
        # game["seasonStageId"]==4 -> playoffs
        #___________________________________________
        
        # skipping games not played yet, and including only main-season.
        if (game.game_utc > TODAY_UTC) or game.stage==1 or game.stage==3:
            continue

        #keeping track of which teams are playing
        #if the game has already been counted, skip


        #away_team
        at=Team.objects.get(team_id=game.a_team)
        #last game recorded
        if len(at.stats[year]['games_played'])>0:
            last_game=at.stats[year]['games_played'][-1]
            last_game_played= schedule.get(game_id=last_game).game_utc
            if last_game_played>=game.game_utc:
                continue
#        if game.game_id in t.stats[year]['games_played']:
#            #game already recorded
#            continue


        #home_team
        ht=Team.objects.get(team_id=game.h_team)
        if len(ht.stats[year]['games_played'])>0:
            last_game=ht.stats[year]['games_played'][-1]
            last_game_played= schedule.get(game_id=last_game).game_utc
            if last_game_played>=game.game_utc:
                continue
        at.stats[year]['games_played'].append(game.game_id)
        at.last_update = TODAY_UTC
        at.save()
        ht.stats[year]['games_played'].append(game.game_id)
        ht.last_update = TODAY_UTC
        ht.save()


        print('\n')

        print('{0} - {1} (id: {2})'.format(game.game_date,game.tricode,game.game_id))

        #_____________________________________________________________
        #fetching the play-by-play of the first period of the game
        #the number '1' at the end of the url refer to the period
        #if you want more than the first period, change that

        #Download the json once, and save it locally.
        #if the script doesn't find it, it will download it again
        pbp_url='http://data.nba.net/prod/v1/{0}/{1}_pbp_1.json'.format(game.game_date,game.game_id)
        pbp_json=get(pbp_url).json()

        #I found a json with no plays. Perhaps a postponed game? Need to investigate.
        if len(pbp_json["plays"])==0:
            Team.objects.get(team_id=game.a_team).stats[year]['games_played'].pop()
            Team.objects.get(team_id=game.h_team).stats[year]['games_played'].pop()
            continue

        #find and record the starters for the game
        pl_start=find_starters(pbp_json,year)
        for _team in pl_start:
            t=Team.objects.get(team_id=_team)
            t.stats[year]['starters'].append(pl_start[_team])
            t.last_update = TODAY_UTC
            t.save()
        print('Starters:')
        print('{: >20} {: >20}'.format(Team.objects.get(team_id=game.a_team).full_name,Team.objects.get(team_id=game.h_team).full_name))
        for _i in range(5):
            try:
                away_p=Player.objects.get(nba_id=pl_start[game.a_team][_i]).last_name
            except:
                away_p=''
            try:
                home_p=Player.objects.get(nba_id=pl_start[game.h_team][_i]).last_name
            except:
                home_p=''
            print('{: >20} {: >20}'.format(away_p,home_p))

        #I keep track of the first 2 plays after the tip-off
        tip_off_found=0
        tip_off_winning_player=''
        for i,play in enumerate(pbp_json["plays"][:10]):
            if play["eventMsgType"]=="10":
                tip_off_found=1
                tip_off=pbp_json["plays"][i]
                play_1=pbp_json["plays"][i+1]
                play_2=pbp_json["plays"][i+2]
                #recording who won the tip-off, and what team got possesion.
                t=Team.objects.get(team_id=tip_off["teamId"])
                tip_off_winning_team=t.full_name
                t.stats[year]['tip_off_won']+=1
                t.last_update = TODAY_UTC
                t.save()
                jumpers=find_jumpers(tip_off,pl_start,year)
#                    if len(jumpers)<2:
#                        if tip_off["personId"] not in jumpers:
#                            jumpers.append(int(tip_off["personId"]))
                for _t in jumpers:
                    if _t==tip_off["teamId"]:
                        p=Player.objects.get(nba_id=jumpers[_t][0])
                        p.jumps_won+=1
                        p.last_update = TODAY_UTC
                        p.save()
                        tip_off_winning_player=[jumpers[_t][0],p.last_name]
                        break
                if tip_off_winning_player=='':
                    print(1,jumpers)
                    sys.exit()
                    for _t in jumpers:
                        if jumpers[_t] in t.stats[year]['jumper_list']:
                            p=Player.objects.get(nba_id=_j)
                            p.jumps_won+=1
                            p.last_update = TODAY_UTC
                            p.save()
                            tip_off_winning_player=[int(_j),p.last_name]
                            break
                
                break
        
        #if tip_off_found==0 -> Jump ball violation
        if tip_off_found==0:
            jumpers={_t:[] for _t in pl_start}
            for i,play in enumerate(pbp_json["plays"][:10]):
                if play["eventMsgType"]=="7":
                    for _team in pl_start:
                        if _team != pbp_json["plays"][i]["teamId"]:
                            t=Team.objects.get(team_id=_team)
                            tip_off_winning_team=t.full_name
                            t.stats[year]['tip_off_won']+=1
                            t.last_update = TODAY_UTC
                            t.save()
                            id_jumper=most_probable_jumper(pl_start[_team])
                            p=Player.objects.get(nba_id=id_jumper)
                            p.jumps_won+=1
                            p.last_update = TODAY_UTC
                            p.save()
                            tip_off_winning_player=[int(id_jumper),p.last_name]
                            jumpers[_team].append(int(id_jumper))
                        else:
                            jumpers[_team].append(int(pbp_json["plays"][i]["personId"]))
                    break
    
        for _t in jumpers:
            if len(jumpers[_t])==0:
                jumpers[_t].append(most_probable_jumper(pl_start[_t]))
                if int(_t)==int(pbp_json["plays"][1]["teamId"]):
                    t=Team.objects.get(team_id=_t)
                    tip_off_winning_team=t.full_name
                    t.stats[year]['tip_off_won']+=1
                    t.last_update = TODAY_UTC
                    t.save()
                    
                    p=Player.objects.get(nba_id=jumpers[_t][0])
                    p.jumps_won+=1
                    p.last_update = TODAY_UTC
                    p.save()
                    tip_off_winning_player=[int(jumpers[_t][0]),p.last_name]
#
#            jumpers=list(set(jumpers))

        print('Jump ball: {0} (id: {1}) vs {2} (id: {3})'.format(Player.objects.get(nba_id=jumpers[game.a_team][0]).last_name, jumpers[game.a_team][0], Player.objects.get(nba_id=jumpers[game.h_team][0]).last_name,jumpers[game.h_team][0]))

        game.jumpers.append(jumpers[game.a_team][0])
        game.jumpers.append(jumpers[game.h_team][0])
        
    
        #checking if the jumpers are recorded jumpers
        for _t in jumpers:
            players=Player.objects.get(nba_id=jumpers[_t][0])
            players.jumps_jumped+=1
            players.last_update = TODAY_UTC
            players.save()
            if not players.is_jumper:
                players.is_jumper=1
                players.last_update = TODAY_UTC
                players.save()
                print('{0} (id: {1}) is now a jumper.'.format(players.last_name,jumpers[_t][0]))

        for _t in jumpers:
            t=Team.objects.get(team_id=_t)
            if jumpers[_t][0]==tip_off_winning_player[0]:
                won=1
            else:
                won=0
            t.stats[year]['jumpers'].append([jumpers[_t][0],won])
            t.save()

            if jumpers[_t][0] not in t.stats[year]['jumper_list']:
                t.stats[year]['jumper_list'].append(jumpers[_t][0])
                t.save()
                s=Player.objects.get(nba_id=jumpers[_t][0]).last_name
                print('{0} (id: {1}) added to the {2} jumpers list.'.format(s,jumpers[_t][0],t.full_name))

        print('{1} (id: {0}) won for {2}.'.format(*tip_off_winning_player,tip_off_winning_team))

        game.jump_win=tip_off_winning_player[0]

        elo1_in=Player.objects.get(nba_id=jumpers[game.a_team][0]).elo_score
        elo2_in=Player.objects.get(nba_id=jumpers[game.h_team][0]).elo_score

        elo1_fi,elo2_fi=updateELO(jumpers[game.a_team][0],jumpers[game.h_team][0],tip_off_winning_player[0])
        
        print('ELO score {} (id: {}) : {:.2f} --> {:.2f}'.format(Player.objects.get(nba_id=jumpers[game.a_team][0]).last_name,jumpers[game.a_team][0],elo1_in,elo1_fi))
        print('ELO score {} (id: {}) : {:.2f} --> {:.2f}'.format(Player.objects.get(nba_id=jumpers[game.h_team][0]).last_name,jumpers[game.h_team][0],elo2_in,elo2_fi))


        #I can use the "eventMsgType" argument to know what happened
        #___________________________________________
        #play["eventMsgType"]==1 -> shot made
        #play["eventMsgType"]==2 -> shot missed
        #play["eventMsgType"]==3 -> free throw
        #play["eventMsgType"]==4 -> rebound
        #play["eventMsgType"]==5 -> turnover
        #play["eventMsgType"]==6 -> foul
        #play["eventMsgType"]==8 -> substitution
        #play["eventMsgType"]==10 -> Jump ball
        #play["eventMsgType"]==12 -> Start period
        #play["eventMsgType"]==20 -> Stoppage: Out-of-Bounds
        #___________________________________________


        #first possession resulted in scoring if the first was a scored shot
        #or the first play was a foul and the second was a scored free throw
        #need to check how missed free throw are recorded
        if play_1["eventMsgType"]=="1" or play_2["eventMsgType"]=="3":
            t=Team.objects.get(team_id=tip_off["teamId"])
            t.stats[year]['scored_first_after_winning_tip_off']+=1
            t.last_update = TODAY_UTC
            t.save()
            print('{0} scored with their first posession after winning the jump ball.'.format(t.full_name))

        #keeping track also if teams tend to make fouls during the first play
        if play_1["eventMsgType"]=="6":
            t=Team.objects.get(team_id=play_1["teamId"])
            t.stats[year]['foul_first_defence']+=1
            t.last_update = TODAY_UTC
            t.save()
            print('{0} commited a foul immediately after losing the jump ball.'.format(t.full_name))

        #________________________________________________________
        #now I want to check who scored first for each team
        #"isScoreChange" record a a change in the score.
        #So I can use that to know when somebody scored.

        #switch to check if someone already scored
        score=0
        shot=0

        #looking at all plays after the tip-off
        for play in pbp_json["plays"][2:]:
            if play["personId"]=='':
                continue
            
            #first shooter
            if shot==0 and play["eventMsgType"] in ["1","2","3"]:
                t=Team.objects.get(team_id=play["teamId"])
                shooter=play["personId"]
                #adding the shooter to the teams list of first shooter.
                #1 -> he made it ; 0 -> he didn't make it
                if play["isScoreChange"]==1:
                    t.stats[year]['first_shooter'].append([shooter,1])
                    print('{0} scored with their first shot.'.format(t.full_name))
                else:
                    t.stats[year]['first_shooter'].append([shooter,0])
                    print('{0} missed their first shot.'.format(t.full_name))
                
                game.all_first_shooters.append(shooter)
                
                #checking if the shot was a 3pt
                if '3pt' in play['description']:
                    t.stats[year]['first_shot_three']+=1
                    print('The shot was a 3-pointer.')
                t.last_update = TODAY_UTC
                t.save()
                
                
                #tracking what team shot already
                #and change the switch that somebody shot
                shooting_team=play["teamId"]
                shot=1
            
            
            if shot==1 and play["eventMsgType"] in ["1","2","3"] and play["teamId"]!= shooting_team:
                t=Team.objects.get(team_id=play["teamId"])
                shooter=play["personId"]
                #adding the shooter to the teams list of first shooter.
                #1 -> he made it ; 0 -> he didn't make it
                if play["isScoreChange"]==1:
                    t.stats[year]['first_shooter'].append([shooter,1])
                    print('{0} scored with their first shot.'.format(t.full_name))
                else:
                    t.stats[year]['first_shooter'].append([shooter,0])
                    print('{0} missed their first shot.'.format(t.full_name))
                
                game.all_first_shooters.append(shooter)
                
                #checking if the shot was a 3pt
                if '3pt' in play['description']:
                    t.stats[year]['first_shot_three']+=1
                    print('The shot was a 3-pointer.')
                t.last_update = TODAY_UTC
                t.save()
                
                shot=2


            #first team score
            if score==0 and play["isScoreChange"]==1:
                t=Team.objects.get(team_id=play["teamId"])
                t.stats[year]['scored_first']+=1
                scorer=play["personId"]
                pl=Player.objects.get(nba_id=scorer).last_name
                #adding the scorer to the teams list of first scorers.
                t.stats[year]['first_scorer'].append(scorer)
                print('{0} scored first, and {1} (id: {2}) was the scorer.'.format(t.full_name,pl,scorer))
                t.last_update = TODAY_UTC
                t.save()
                
                game.all_first_scorers.append(scorer)
                game.player_first_score=scorer
                game.team_first_score=play["teamId"]
                #tracking what team scored already
                #and change the switch that somebody scored
                scoring_team=play["teamId"]
                score=1
        
            #second team scored, if somebody scored
            #and the team is not the one which scored already
            if score==1 and play["isScoreChange"]==1 and play["teamId"]!= scoring_team:
                t=Team.objects.get(team_id=play["teamId"])
                scorer=play["personId"]
                pl=Player.objects.get(nba_id=scorer).last_name
                #adding the scorer to the teams list of first scorers.
                print('{1} (id: {2}) scored first for {0}.'.format(t.full_name,pl,scorer))
                t.stats[year]['first_scorer'].append(scorer)
                t.last_update = TODAY_UTC
                t.save()
                
                game.all_first_scorers.append(scorer)
                #both team scored, so I con exit the loop
                break

        game.save()
    #End of collecting data
    #########




class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument("--year",
                            help="Year for NBA data",
                            required=True, type=int)



    def handle(self, *args, **options):
        update_stats(options["year"])



