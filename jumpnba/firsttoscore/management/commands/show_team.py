#!/usr/bin/env python
from operator import itemgetter
import sys,json,os,argparse

from django.core.management.base import BaseCommand, CommandError
from players.models import Player
from teams.models import Team

class Command(BaseCommand):
    help = 'Show info about team'

    def add_arguments(self, parser):
        parser.add_argument("team",help="Team name",nargs="*")
        parser.add_argument("--year",
                            help="Year for data. If not given, all year will be shown", type=int)

    def print_out(self,_field, _value1):
        print('{: <38} {: <}'.format(_field,_value1))

    def printer(self,_line,percentage=0,player_list=0):
        value1=value2=''
        field=_line[0]
        
        #team stats printer
        if player_list==0:
            number1=_line[1]
            reference1=_line[2]
            value1= '{:>2}/{:>3}'.format(number1,reference1)
            if percentage==1 and reference1!=0:
                value1= value1 +' ({: >5.1f}%)'.format(100.*number1/reference1)
    
            self.print_out(field, value1)
    
        #player list printer
        else:
            pl_list1=_line[1]
        
            for i in range(len(pl_list1)):
                pl_id1=pl_list1[i]
                last_name1=Player.objects.get(nba_id=pl_id1)
                
                if len(pl_list1[i])==3:
                    value1='{: >22} {: >2}/{: >2}'.format(last_name1,pl_list1[i][0],pl_list1[i][1])
                else:
                    value1='{: >22} {: >5}'.format(last_name1,pl_list1[i][0])
                
                if pl_id1=='':
                    value1='{: >38}'.format('')

    def starters(self,_id,_st_list):
        n=0
        for g in _st_list:
            if int(_id) in g:
                n+=1

        return n

    def handle(self, *args, **options):
        
        for _t in Team.objects.all():
            if options["team"][0] in _t.names:
                t=_t
                break
        
        
        if options["year"]:
            year_list=[options["year"]]
        else:
            year_list=[2017,2018,2019,2020]

        #print("--- {0} ---".format(t.full_name))
        os.system('cat ascii_logos/{0}.ascii'.format(t.names[1]))
        print("\n")
        for _y in year_list:
            print("Year {0}:".format(_y))
            d=t.stats[str(_y)]
            gp=len(d['starters'])
            #self.print_out("- Games played:",gp)
            
            self.printer(['- Tip offs won:',d['tip_off_won'],gp],percentage=1) #,.3,.7)
            self.printer(['- Scored first after winning tip off:',d['scored_first_after_winning_tip_off'],d['tip_off_won']],percentage=1) #.2,.5)
            self.printer(['- Scored first:',d['scored_first'],gp],percentage=1)
            self.printer(['- First shot three:',d['first_shot_three'],gp],percentage=1)
            self.printer(['- Foul during first defence:',d['foul_first_defence'],gp],percentage=1)
            
            print('\n'+' - '*21)
            print('Jumpers')
            for _s in d['jumper_list']:
                p=Player.objects.get(nba_id=_s)
                print('- {}   elo: {:.2f} ({} jumps)'.format(p.last_name,p.elo_score,p.jumps_jumped))
#            for i,el in enumerate(d['jumpers']):
#                print(i,el)

            print('\n'+' - '*21)
            print('First shooters')
            sh={}
            for _s in d['first_shooter']:
                if _s[0] not in sh:
                    sh[_s[0]]=[_s[0],0,0]
                sh[_s[0]][1]+=1
                sh[_s[0]][2]+=_s[1]
            
            sh=sorted([sh[el] for el in sh], reverse=True,key=itemgetter(2,1))
            
            for _s in sh:
                p=Player.objects.get(nba_id=_s[0])
                start=self.starters(_s[0],d['starters'])
                print('- {} {}/{} over {} games started.'.format(p.last_name,_s[2],_s[1],start))
            
            print('\n'+' - '*21)
            print('First scorers')
            sc={}
            for _s in d['first_scorer']:
                if _s not in sc:
                    sc[_s]=[_s,0]
                sc[_s][1]+=1
            
            sc=sorted([sc[el] for el in sc], reverse=True,key=itemgetter(1))
            
            for _s in sc:
                p=Player.objects.get(nba_id=_s[0])
                start=self.starters(_s[0],d['starters'])
                print('- {} {} over {} games started.'.format(p.last_name,_s[1],start))
        
            print('\n'+' - '*21)

#        print('Times that winning the tip-off resulted in the team scoring first:')
#        print(tot_score_first_possession,'/',tot_games,' (','%.1f'%(100.*tot_score_first_possession/tot_games),'%)',sep='')


#        print('\n')



 