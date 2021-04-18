#!/usr/bin/env python
from datetime import timedelta
from operator import itemgetter
import argparse,pytz

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from firsttoscore.models import Player
from firsttoscore.models import Team
from firsttoscore.models import Game
from firsttoscore.management.commands.update_stats import compareRating
from firsttoscore.management.commands.update_stats import update_stats
from firsttoscore.management.commands.update_players import update_players
from firsttoscore.management.commands.update_schedule import update_schedule

__author__ = 'Giacomo Terreran <gqterre@gmail.com>'
__credits__ = ['Scott Coughlin <scottcoughlin2014@u.northwestern.edu>',
               'Kyle Kremer <kylekremer23@gmail.com>']

def scoring_first_probability(pj,oe_a,oe_h):
    #pj is the probability that the away team win the tip-off

    #team 1 has pj_1 probability to win the tip off and then oe_1 to score.
    #so the probability to win the tip-off and scoring immediately after is
    #p=pj_1*oe_1
    #the losing team will have a probability to score on their first posession if
    #first the other team miss (1-oe_1) and then they score (oe_2)
    #p=pj_1*(1-oe_1)*(oe_2)
    
    
    team_a_probability=0
    team_h_probability=0
    #k-th posession for the team which won the tip-off
    #j-th posession for the team which won the tip-off
    k=0
    j=0
    while 1:
        if k==j:
            team_a_probability= team_a_probability + pj * (1-oe_a)**k * (1-oe_h)**j * oe_a
            team_h_probability= team_h_probability + (1-pj) * (1-oe_h)**k * (1-oe_a)**j * oe_h
            k+=1
        else:
            team_h_probability= team_h_probability + pj * (1-oe_a)**k * (1-oe_h)**j * oe_h
            team_a_probability= team_a_probability + (1-pj) * (1-oe_h)**k * (1-oe_a)**j * oe_a
            j+=1

        if 1.-(team_a_probability+team_h_probability)<1e-7:
            break
    return team_a_probability

def print_out(_field, _value1, _value2):
    print('{: >35} {: >27} {: >27}'.format(_field,_value1,_value2))

def printer(_line,percentage=0,player_list=0):
    value1=value2=''
    field=_line[0]
    
    #team stats printer
    if player_list==0:
        number1=_line[1]
        reference1=_line[2]
        value1= ' '*23+'{:>2}/{:>3}'.format(number1,reference1)
        if percentage==1 and reference1!=0:
            value1= value1 +' ({: >5.1f}%)'.format(100.*number1/reference1)
        

        number2=_line[3]
        reference2=_line[4]
        value2= ' '*23+'{:>2}/{:>3}'.format(number2,reference2)
        if percentage==1 and reference2!=0:
            value2= value2 +' ({: >5.1f}%)'.format(100.*number2/reference2)

        print_out(field, value1, value2)

def show_games(_year,tomorrow=0):
    
    print("Looking for player updates")
    update_players(_year)
    
    print("Looking for schedule updates")
    update_schedule(_year)
    
    print("Looking for game updates")
    update_stats(_year)

    #Checking what games are played today
    
    TODAY_UTC = timezone.now()
    eastern = pytz.timezone('US/Eastern')
    TODAY = TODAY_UTC.astimezone(eastern)
    
    if tomorrow:
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
    
    schedule=Game.objects.filter(season=_year)

    #scrolling through the games
    game_counter=0
    for i,game in enumerate(schedule):
        if game.game_date!=date_check:continue
        
        game_counter+=1
        game_time='GAME {} - {}'.format(game_counter,game.game_time)
        a_team=Team.objects.get(team_id=game.a_team)
        h_team=Team.objects.get(team_id=game.h_team)
        a_team_name=a_team.full_name
        h_team_name=h_team.full_name
        print('\n')
        print('{: >35} {: >38} {: >38}'.format(game_time,a_team_name,h_team_name))
        print("_"*113)
        h_d=h_team.stats[str(_year)]
        a_d=a_team.stats[str(_year)]
        h_gp=len(h_d['starters'])
        a_gp=len(a_d['starters'])
        printer(['Tip offs won:',a_d['tip_off_won'],a_gp, h_d['tip_off_won'],h_gp],percentage=1) #,.3,.7)
        printer(['Scored first after winning tip off:',a_d['scored_first_after_winning_tip_off'],a_d['tip_off_won'], h_d['scored_first_after_winning_tip_off'],h_d['tip_off_won']],percentage=1) #.2,.5)
        
        printer(['Scored first:',a_d['scored_first'],a_gp, h_d['scored_first'],h_gp],percentage=1)
        printer(['First shot three:',a_d['first_shot_three'],a_gp, h_d['first_shot_three'],h_gp],percentage=1)
        printer(['Foul during first defence:',a_d['foul_first_defence'],a_gp, h_d['foul_first_defence'],h_gp],percentage=1)

        total_shots=[0,0]
        total_shots_made=[0,0]
        for i,d in enumerate([a_d,h_d]):
            for _s in d['first_shooter']:
                total_shots[i]+=1
                total_shots_made[i]+=_s[1]
    
        printer(['Offensive efficiency:',total_shots_made[0],total_shots[0],total_shots_made[1],total_shots[1]],percentage=1)
        a_offensive_efficiency=total_shots_made[0]/total_shots[0]
        h_offensive_efficiency=total_shots_made[1]/total_shots[1]
        
        #print('{: >35} {: >28.2f}% {: >45.2f}%'.format('Offensive efficiency:',a_offensive_efficiency*100.,h_offensive_efficiency*100.))
        
        
        print('\n'+' - '*21)
        out=[[],[]]
        for i,d in enumerate([a_d,h_d]):
            for _s in d['jumper_list']:
                p=Player.objects.get(nba_id=_s)
                #out[i].append('- {}   elo: {:.2f} ({} jumps)'.format(p.last_name,p.elo_score,p.jumps_jumped))
                out[i].append([p.last_name,p.elo_score,p.jumps_jumped])

        out[0]=sorted(out[0],reverse=1,key=itemgetter(1))
        out[1]=sorted(out[1],reverse=1,key=itemgetter(1))
        
        for i in range(max([len(out[0]),len(out[1])])):
            if i>len(out[0])-1:
                value1='{: >44}'.format('')
            else:
                value1='{: >22} - {: >7.2f} ({: >3} jumps)'.format(out[0][i][0],out[0][i][1],out[0][i][2])
            if i>len(out[1])-1:
                value2='{: >44}'.format('')
            else:
                value2='{: >22} - {: >7.2f} ({: >3} jumps)'.format(out[1][i][0],out[1][i][1],out[1][i][2])
            
            if i==0:
                print_out('Jumpers:', value1, value2)
            else:
                print_out('', value1, value2)

        print('\n')
        for aj in out[0]:
            for hj in out[1]:
                p=compareRating(aj[1],hj[1])
                scoring_first=scoring_first_probability(p,a_offensive_efficiency,h_offensive_efficiency)
                if scoring_first<0.5:
                    am_p=100.*(1.-scoring_first)/scoring_first
                else:
                    am_p=-100.*scoring_first/(1.-scoring_first)
                value1='{} has {:.2f}% of probability of beat {}. {} have a probability of {:.2f}% ({:+.0f}) to score first.'.format(aj[0],p*100,hj[0],a_team_name,scoring_first*100,am_p)
                print(value1)





        print('\n'+' - '*21)
        sh=[{},{}]
        for i,d in enumerate([a_d,h_d]):
            for _s in d['first_shooter']:
                if _s[0] not in sh[i]:
                    sh[i][_s[0]]=[_s[0],0,0]
                sh[i][_s[0]][1]+=1
                sh[i][_s[0]][2]+=_s[1]
        

        sh[0]=sorted([sh[0][el] for el in sh[0]], reverse=True,key=itemgetter(2,1))
        sh[1]=sorted([sh[1][el] for el in sh[1]], reverse=True,key=itemgetter(2,1))

        for i in range(max([len(sh[0]),len(sh[1])])):
            if i>len(sh[0])-1:
                value1='{: >28}'.format('')
            else:
                p=Player.objects.get(nba_id=sh[0][i][0])
                value1='{: >22} {: >2}/{: >2}'.format(p.last_name,sh[0][i][2],sh[0][i][1])
            if i>len(sh[1])-1:
                value2='{: >28}'.format('')
            else:
                p=Player.objects.get(nba_id=sh[1][i][0])
                value2='{: >22} {: >2}/{: >2}'.format(p.last_name,sh[1][i][2],sh[1][i][1])
            
            if i==0:
                print_out('First shooters:', value1, value2)
            else:
                print_out('', value1, value2)

        print('\n')


        print('\n'+' - '*21)
        sc=[{},{}]
        for i,d in enumerate([a_d,h_d]):
            for _s in d['first_scorer']:
                if _s not in sc[i]:
                    sc[i][_s]=[_s,0]
                sc[i][_s][1]+=1

        sc[0]=sorted([sc[0][el] for el in sc[0]], reverse=True,key=itemgetter(1))
        sc[1]=sorted([sc[1][el] for el in sc[1]], reverse=True,key=itemgetter(1))

        for i in range(max([len(sc[0]),len(sc[1])])):
            if i>len(sc[0])-1:
                value1='{: >27}'.format('')
            else:
                p=Player.objects.get(nba_id=sc[0][i][0])
                value1='{: >22} {: >2}'.format(p.last_name,sc[0][i][1])
            if i>len(sc[1])-1:
                value2='{: >27}'.format('')
            else:
                p=Player.objects.get(nba_id=sc[1][i][0])
                value2='{: >22} {: >2}'.format(p.last_name,sc[1][i][1])
            
            if i==0:
                print_out('First scorer:', value1, value2)
            else:
                print_out('', value1, value2)

        print('\n')




class Command(BaseCommand):
    help = 'Show matchups'

    def add_arguments(self, parser):
        parser.add_argument("--year",
                            help="Year for NBA data",
                            required=True, type=int)
                            
        parser.add_argument("--tomorrow", help="Show tomorrow games instead of today's", default=0, action='store_true')


    


    def handle(self, *args, **options):
        show_games(options["year"],options["tomorrow"])


