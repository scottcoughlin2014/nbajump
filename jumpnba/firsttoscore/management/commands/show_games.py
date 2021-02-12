#!/usr/bin/env python
from datetime import datetime,timedelta,date
from operator import itemgetter
import sys,json,os,argparse,pytz

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from players.models import Player
from teams.models import Team
from games.models import Game

class Command(BaseCommand):
    help = 'Show matchups'

    def compareRating(self,_player_elo, _opponent_elo):
        """
        Compares the two ratings of the this player and the opponent.
        @param opponent - the player to compare against.
        @returns - The expected score between the two players.
        """
        return ( 1+10**( ( _opponent_elo-_player_elo )/400.0 ) ) ** -1

    def add_arguments(self, parser):
        parser.add_argument("--year",
                            help="Year for NBA data",
                            required=True, type=int)
                            
        parser.add_argument("--tomorrow", help="Show tomorrow games instead of today's", default=0, action='store_true')

    def print_out(self,_field, _value1, _value2):
        print('{: >35} {: >27} {: >27}'.format(_field,_value1,_value2))

    def printer(self,_line,percentage=0,player_list=0):
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
    
            self.print_out(field, value1, value2)
    


    def handle(self, *args, **options):
        #Checking what games are played today
        
        TODAY_UTC = timezone.now()
        eastern = pytz.timezone('US/Eastern')
        TODAY = TODAY_UTC.astimezone(eastern)
        
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
        
        schedule=Game.objects.filter(season=options["year"])
    
        #scrolling through the games
        game_counter=0
        for i,game in enumerate(schedule):
            if game.game_date!=date_check:continue
            
            game_counter+=1
            game_time='GAME {} - {} (Eastern time)'.format(game_counter,game.game_date)
            a_team=Team.objects.get(team_id=game.a_team)
            h_team=Team.objects.get(team_id=game.h_team)
            a_team_name=a_team.full_name
            h_team_name=h_team.full_name
            print('\n')
            print('{: >35} {: >38} {: >38}'.format(game_time,a_team_name,h_team_name))
            print("_"*113)
            h_d=h_team.stats[str(options["year"])]
            a_d=a_team.stats[str(options["year"])]
            h_gp=len(h_d["games_played"])
            a_gp=len(a_d["games_played"])
            self.printer(['Tip offs won:',a_d['tip_off_won'],a_gp, h_d['tip_off_won'],h_gp],percentage=1) #,.3,.7)
            self.printer(['Scored first after winning tip off:',a_d['scored_first_after_winning_tip_off'],a_d['tip_off_won'], h_d['scored_first_after_winning_tip_off'],h_d['tip_off_won']],percentage=1) #.2,.5)
            self.printer(['Scored first:',a_d['scored_first'],a_gp, h_d['scored_first'],h_gp],percentage=1)
            self.printer(['First shot three:',a_d['first_shot_three'],a_gp, h_d['first_shot_three'],h_gp],percentage=1)
            self.printer(['Foul during first defence:',a_d['foul_first_defence'],a_gp, h_d['foul_first_defence'],h_gp],percentage=1)

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
                    self.print_out('Jumpers:', value1, value2)
                else:
                    self.print_out('', value1, value2)

            print('\n')
            for aj in out[0]:
                for hj in out[1]:
                    p=self.compareRating(aj[1],hj[1])*100
                    value1='{} has {:.2f}% of probability of beat {}.'.format(aj[0],p,hj[0])
                    self.print_out('', value1, '')



            


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
                    self.print_out('First shooters:', value1, value2)
                else:
                    self.print_out('', value1, value2)

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
                    self.print_out('First scorer:', value1, value2)
                else:
                    self.print_out('', value1, value2)

            print('\n')


