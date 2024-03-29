from django.shortcuts import render
from datetime import datetime,timedelta,date
from operator import itemgetter
import sys,json,os,argparse,pytz
import requests

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from firsttoscore.models import Player
from firsttoscore.models import Team
from firsttoscore.models import Game
from firsttoscore.management.commands.update_stats import compareRating
from firsttoscore.management.commands.update_stats import update_stats
from firsttoscore.management.commands.update_players import update_players
from firsttoscore.management.commands.get_odds import get_odds
from firsttoscore.management.commands.update_schedule import update_schedule
from firsttoscore.management.commands.show_games import scoring_first_probability

from .utils import get_plot
from .utils import compare_colors

from django.shortcuts import redirect

__author__ = 'Giacomo Terreran <gqterre@gmail.com>'
__credits__ = ['Scott Coughlin <scottcoughlin2014@u.northwestern.edu>',
               'Kyle Kremer <kylekremer23@gmail.com>']

def redirect_home(request):
    response = redirect('/today')
    return response


def todays_games(request,day):
    _year=2020
    
    if day=='tomorrow': tomorrow=1
    else: tomorrow=0
    
    view={'games':[],'teams':[],'showing_day':day}
    for _t in Team.objects.all():
        view['teams'].append({
        'team_id':_t.team_id,
        'nick':_t.names[0],
        's_logo':'images/s_{}.png'.format(_t.tricode)
        })

    update_players(_year)

    update_schedule(_year)
    
    update_stats(_year)

    #get_odds()

    #Checking what games are played today
    
    TODAY_UTC = timezone.now()
    #TODAY_UTC = datetime.strptime('2021-03-11', '%Y-%m-%d')
    eastern = pytz.timezone('US/Eastern')
    TODAY = TODAY_UTC.astimezone(eastern)
    print(TODAY)
    
    if tomorrow:
        date_to_show="|"+" "*47+"TOMORROW'S GAMES"+" "*48+"|"
        TOMORROW = TODAY + timedelta(days=1)
        date_check=TOMORROW.strftime("%Y%m%d")
    else:
        date_to_show="|"+" "*49+"TODAY'S GAMES"+" "*49+"|"
        date_check=TODAY.strftime("%Y%m%d")

    print(date_check)
    schedule=Game.objects.filter(season=_year)

    #scrolling through the games
    game_counter=0
    for i,game in enumerate(schedule):
        if game.game_date!=date_check:continue
        game_counter+=1
        if game_counter==1:
            active='active'
        else:
            active=''
        a_team=Team.objects.get(team_id=game.a_team)
        h_team=Team.objects.get(team_id=game.h_team)
        a_team_name=a_team.full_name
        h_team_name=h_team.full_name
        a_color=a_team.colors[0]
        if compare_colors(a_team.colors[0],h_team.colors[0]):
            h_color=h_team.colors[0]
        else:
            h_color=h_team.colors[1]
        view['games'].append({
        'active':active,
        'h_odds' : game.h_odds,
        'a_odds' : game.a_odds,
        'time':game.game_time.split()[0]+' ET',
        'a_tri':game.tricode[:3],
        'h_tri':game.tricode[3:],
        'a_team':Team.objects.get(team_id=game.a_team),
        'h_team':Team.objects.get(team_id=game.h_team),
        'a_team_name':a_team.full_name,
        'h_team_name':h_team.full_name,
        'in_tag':'#'+game.tricode,
        'out_tag':game.tricode,
        'a_s_logo':'images/s_{}.png'.format(game.tricode[:3]),
        'h_s_logo':'images/s_{}.png'.format(game.tricode[3:]),
        'a_logo':'images/{}.png'.format(game.tricode[:3]),
        'h_logo':'images/{}.png'.format(game.tricode[3:])
        })

        h_d=h_team.stats[str(_year)]
        a_d=a_team.stats[str(_year)]
        h_gp=len(h_d['starters'])
        a_gp=len(a_d['starters'])
       
        view['games'][-1]['away_tip_off_won']=a_d['tip_off_won']
        view['games'][-1]['away_game_played']=a_gp
        view['games'][-1]['away_tip_off_won_p']='{:.1f}'.format(a_d['tip_off_won']/a_gp*100.)
        view['games'][-1]['home_tip_off_won']=h_d['tip_off_won']
        view['games'][-1]['home_game_played']=h_gp
        view['games'][-1]['home_tip_off_won_p']='{:.1f}'.format(h_d['tip_off_won']/h_gp*100.)

        view['games'][-1]['away_scored_first_after_winning_tip_off']=a_d['scored_first_after_winning_tip_off']
        view['games'][-1]['away_scored_first_after_winning_tip_off_p']='{:.1f}'.format(a_d['scored_first_after_winning_tip_off']/a_d['tip_off_won']*100.)
        view['games'][-1]['home_scored_first_after_winning_tip_off']=h_d['scored_first_after_winning_tip_off']
        view['games'][-1]['home_scored_first_after_winning_tip_off_p']='{:.1f}'.format(h_d['scored_first_after_winning_tip_off']/h_d['tip_off_won']*100.)

        view['games'][-1]['away_scored_first']=a_d['scored_first']
        view['games'][-1]['away_scored_first_p']='{:.1f}'.format(a_d['scored_first']/a_gp*100.)
        view['games'][-1]['home_scored_first']=h_d['scored_first']
        view['games'][-1]['home_scored_first_p']='{:.1f}'.format(h_d['scored_first']/h_gp*100.)

        view['games'][-1]['away_first_shot_three']=a_d['first_shot_three']
        view['games'][-1]['away_first_shot_three_p']='{:.1f}'.format(a_d['first_shot_three']/a_gp*100.)
        view['games'][-1]['home_first_shot_three']=h_d['first_shot_three']
        view['games'][-1]['home_first_shot_three_p']='{:.1f}'.format(h_d['first_shot_three']/h_gp*100.)


        view['games'][-1]['away_foul_first_defence']=a_d['foul_first_defence']
        view['games'][-1]['away_foul_first_defence_p']='{:.1f}'.format(a_d['foul_first_defence']/a_gp*100.)
        view['games'][-1]['home_foul_first_defence']=h_d['foul_first_defence']
        view['games'][-1]['home_foul_first_defence_p']='{:.1f}'.format(h_d['foul_first_defence']/h_gp*100.)


        total_shots=[0,0]
        total_shots_made=[0,0]
        for i,d in enumerate([a_d,h_d]):
            for _s in d['first_shooter'][-10:]:
                total_shots[i]+=1
                total_shots_made[i]+=_s[1]
    

        view['games'][-1]['away_shot_made']=total_shots_made[0]
        view['games'][-1]['away_total_shots']=total_shots[0]
        view['games'][-1]['away_shot_made_p']='{:.1f}'.format(total_shots_made[0]/total_shots[0]*100.)
        view['games'][-1]['home_shot_made']=total_shots_made[1]
        view['games'][-1]['home_total_shots']=total_shots[1]
        view['games'][-1]['home_shot_made_p']='{:.1f}'.format(total_shots_made[1]/total_shots[1]*100.)


        a_offensive_efficiency=total_shots_made[0]/total_shots[0]
        h_offensive_efficiency=total_shots_made[1]/total_shots[1]

        
        out=[[],[]]
        for i,tt in enumerate([a_team,h_team]):
            d=tt.stats[str(_year)]
            for _s in d['jumper_list']:
                p=Player.objects.get(nba_id=_s)
                if int(p.team_id)!=int(tt.team_id):
                    continue
                out[i].append([p.last_name,p.elo_score,p.jumps_jumped,p.nba_id])

        out[0]=sorted(out[0],reverse=1,key=itemgetter(2))
        out[1]=sorted(out[1],reverse=1,key=itemgetter(2))
        
        #keep only the most experienced jumper and the last who jumped in the last 5 games, different than the most experienced.

        view['games'][-1]['away_jumpers']=[]
        for _j in out[0]:
            view['games'][-1]['away_jumpers'].append({'name':_j[0],'elo':'{:.0f}'.format(_j[1]),'jumps':_j[2]})

        view['games'][-1]['home_jumpers']=[]
        for _j in out[1]:
            view['games'][-1]['home_jumpers'].append({'name':_j[0],'elo':'{:.0f}'.format(_j[1]),'jumps':_j[2]})


        # compare against projected starters
        if game.projected_starters:
            for i,d in enumerate([a_d,h_d]):
                new_out=[]
                for _s in d['jumper_list']:
                    if _s in game.projected_starters:
                        p=Player.objects.get(nba_id=_s)
                        new_out.append([p.last_name,p.elo_score,p.jumps_jumped,p.nba_id])
                out[i]=sorted(new_out,reverse=1,key=itemgetter(2))

        for i,d in enumerate([a_d,h_d]):
            if len(out[i])==1: #already only 1 jumper is playing. No brainer
                continue
            elif len(out[i])==0: #no jumpers playing. Problem
                break
            else:
                most_experienced_jumper=out[i][0]
                new_out=[most_experienced_jumper]
                for _s in d['jumpers'][:-6:-1]:
                    if int(most_experienced_jumper[-1])!=int(_s[0]):
                        p=Player.objects.get(nba_id=_s[0])
                        new_out.append([p.last_name,p.elo_score,p.jumps_jumped,p.nba_id])
                        break
                out[i]=new_out


        view['games'][-1]['away_elo_off']=a_d['elo_off']
        view['games'][-1]['away_elo_def']=a_d['elo_def']
        view['games'][-1]['home_elo_off']=h_d['elo_off']
        view['games'][-1]['home_elo_def']=h_d['elo_def']


        view['games'][-1]['probs']=[]

        for aj in out[0]:
            for hj in out[1]:
                #probability that the away jumper win the tip-off
                p=compareRating(aj[1],hj[1])
                
                #probabulity that away offense score vs the home defence
                p_ah=compareRating(a_d['elo_off'],h_d['elo_def'])
                #probabulity that home offense score vs the away defence
                p_ha=compareRating(h_d['elo_off'],a_d['elo_def'])
                
                
                #probabilty that the away team score first
                #scoring_first=scoring_first_probability(p,a_offensive_efficiency,h_offensive_efficiency)
                scoring_first=scoring_first_probability(p,p_ah,p_ha)
                if scoring_first<0.5:
                    if scoring_first==0:
                        am_p=10000
                    else:
                        am_p=100.*(1.-scoring_first)/scoring_first
                else:
                    am_p=-100.*scoring_first/(1.-scoring_first)
                view['games'][-1]['probs'].append({'j1':aj[0],'j2':hj[0],'pj1':'{:.1f}'.format(p*100),'pj2':'{:.1f}'.format((1-p)*100),'team1':a_team.tricode,'ps1':'{:.1f}'.format(scoring_first*100),'am1':'{:.0f}'.format(am_p),'team2':h_team.tricode,'ps2':'{:.1f}'.format((1-scoring_first)*100),'am2':'{:.0f}'.format(-am_p),'chart_pl':get_plot(p,a_color,h_color),'chart_te':get_plot(scoring_first,a_color,h_color)})




        sh=[{},{}]
        for i,d in enumerate([a_d,h_d]):
            for _s in d['first_shooter']:
                if _s[0] not in sh[i]:
                    sh[i][_s[0]]=[_s[0],0,0]
                sh[i][_s[0]][1]+=1
                sh[i][_s[0]][2]+=_s[1]
        

        sh[0]=sorted([sh[0][el] for el in sh[0]], reverse=True,key=itemgetter(2,1))
        sh[1]=sorted([sh[1][el] for el in sh[1]], reverse=True,key=itemgetter(2,1))

        view['games'][-1]['away_shooters']=[]
        for _j in sh[0]:
            view['games'][-1]['away_shooters'].append({'name':Player.objects.get(nba_id=_j[0]).last_name,'made':_j[2],'total':_j[1],'percentage':'{:.1f}'.format(100*_j[2]/_j[1])})

        view['games'][-1]['home_shooters']=[]
        for _j in sh[1]:
            view['games'][-1]['home_shooters'].append({'name':Player.objects.get(nba_id=_j[0]).last_name,'made':_j[2],'total':_j[1],'percentage':'{:.1f}'.format(100*_j[2]/_j[1])})
            



        sc=[{},{}]
        for i,d in enumerate([a_d,h_d]):
            for _s in d['first_scorer']:
                if _s not in sc[i]:
                    sc[i][_s]=[_s,0]
                sc[i][_s][1]+=1

        sc[0]=sorted([sc[0][el] for el in sc[0]], reverse=True,key=itemgetter(1))
        sc[1]=sorted([sc[1][el] for el in sc[1]], reverse=True,key=itemgetter(1))

        view['games'][-1]['away_scorers']=[]
        for _j in sc[0]:
            view['games'][-1]['away_scorers'].append({'name':Player.objects.get(nba_id=_j[0]).last_name,'made':_j[1]})

        view['games'][-1]['home_scorers']=[]
        for _j in sc[1]:
            view['games'][-1]['home_scorers'].append({'name':Player.objects.get(nba_id=_j[0]).last_name,'made':_j[1]})
            

    
    return render(request, 'index.html', context=view)


def starters(_id,_st_list):
    n=0
    for g in _st_list:
        if int(_id) in g:
            n+=1

    return n


def team_page(request,team_id):
    t=Team.objects.get(team_id=team_id)
    
    context={'year':[],'teams':[],'team':t.full_name,'logo':'images/'+t.tricode+'.png'}
    
    for _t in Team.objects.all():
        context['teams'].append({
        'team_id':_t.team_id,
        'nick':_t.names[0],
        's_logo':'images/s_{}.png'.format(_t.tricode)
        })
    
    
    
    year_list=[2017,2018,2019,2020]

    for _y in year_list[::-1]:
        
        context['year'].append({'year':_y})
        d=t.stats[str(_y)]
        gp=len(d['starters'])
        
        context['year'][-1]['tip_off_won']=d['tip_off_won']
        context['year'][-1]['game_played']=gp
        context['year'][-1]['tip_off_won_p']='{:.1f}'.format(d['tip_off_won']/gp*100.)
        
        context['year'][-1]['scored_first_after_winning_tip_off']=d['scored_first_after_winning_tip_off']
        context['year'][-1]['scored_first_after_winning_tip_off_p']='{:.1f}'.format(d['scored_first_after_winning_tip_off']/d['tip_off_won']*100.)

        context['year'][-1]['scored_first']=d['scored_first']
        context['year'][-1]['scored_first_p']='{:.1f}'.format(d['scored_first']/gp*100.)

        context['year'][-1]['first_shot_three']=d['first_shot_three']
        context['year'][-1]['first_shot_three_p']='{:.1f}'.format(d['first_shot_three']/gp*100.)


        context['year'][-1]['foul_first_defence']=d['foul_first_defence']
        context['year'][-1]['foul_first_defence_p']='{:.1f}'.format(d['foul_first_defence']/gp*100.)


        total_shots=0
        total_shots_made=0
        for _s in d['first_shooter']:
            total_shots+=1
            total_shots_made+=_s[1]
    

        context['year'][-1]['shot_made']=total_shots_made
        context['year'][-1]['total_shots']=total_shots
        context['year'][-1]['shot_made_p']='{:.1f}'.format(total_shots_made/total_shots*100.)

        context['year'][-1]['elo_off']=d['elo_off']
        context['year'][-1]['elo_def']=d['elo_def']


        context['year'][-1]['jumpers']=[]
        
        for _s in d['jumper_list']:
            p=Player.objects.get(nba_id=_s)
            if int(p.team_id)!=int(team_id):
                continue
            context['year'][-1]['jumpers'].append({'name':p.last_name,'elo':'{:.0f}'.format(p.elo_score),'jumps':p.jumps_jumped})


        context['year'][-1]['l5_jumpers']=[]
        for _s in d['jumpers'][:-6:-1]:
            p=Player.objects.get(nba_id=_s[0])
            if _s[1]==1:
                made='won'
            else:
                made='lost'
            context['year'][-1]['l5_jumpers'].append({'name':p.last_name,'made':made})



        sh={}
        for _s in d['first_shooter']:
            if _s[0] not in sh:
                sh[_s[0]]=[_s[0],0,0]
            sh[_s[0]][1]+=1
            sh[_s[0]][2]+=_s[1]

        sh=sorted([sh[el] for el in sh], reverse=True,key=itemgetter(2,1))

        context['year'][-1]['shooters']=[]
        for _s in sh:
            p=Player.objects.get(nba_id=_s[0])
            start=starters(_s[0],d['starters'])
            context['year'][-1]['shooters'].append({'name':Player.objects.get(nba_id=_s[0]).last_name,'made':_s[2],'total':_s[1],'percentage':'{:.1f}'.format(100*_s[2]/_s[1])})

        context['year'][-1]['l5_shooters']=[]
        for _s in d['first_shooter'][:-6:-1]:
            p=Player.objects.get(nba_id=_s[0])
            if _s[1]==1:
                made='made'
            else:
                made='missed'
            context['year'][-1]['l5_shooters'].append({'name':p.last_name,'made':made})



        sc={}
        for _s in d['first_scorer']:
            if _s not in sc:
                sc[_s]=[_s,0]
            sc[_s][1]+=1

        sc=sorted([sc[el] for el in sc], reverse=True,key=itemgetter(1))

        context['year'][-1]['scorers']=[]
        for _s in sc:
            p=Player.objects.get(nba_id=_s[0])
            start=starters(_s[0],d['starters'])
            context['year'][-1]['scorers'].append({'name':Player.objects.get(nba_id=_s[0]).last_name,'made':_s[1]})

        context['year'][-1]['l5_scorers']=[]
        for _s in d['first_scorer'][:-6:-1]:
            p=Player.objects.get(nba_id=_s)
            context['year'][-1]['l5_scorers'].append({'name':p.last_name})


    return render(request, 'team_page.html', context=context)


def elo_standing(request):
    
    context={'list':[], 'teams':[]}
    
    for t in Team.objects.all():
        context['teams'].append({
        'team_id':t.team_id,
        'nick':t.names[0],
        's_logo':'images/s_{}.png'.format(t.tricode)
        })
    

    ss=[]
    for p in Player.objects.filter(is_jumper=1):
        ss.append([p.first_name,p.last_name,p.elo_score,p.jumps_jumped])

    for el in sorted(ss,reverse=True,key=itemgetter(2)):
        context['list'].append({'first':el[0], 'last':el[1], 'elo':'{:.0f}'.format(el[2]),'jumps':el[3]})
    return render(request, 'elo_standing.html', context=context)

def elo_compare(request):

    context={
        'teams':[],
        'teams_sel':[],
        'players_sel':[],
        'elos':[]
    }

    
    for t in Team.objects.all():
        context['teams_sel'].append({'team_id':t.team_id,'full_name':t.full_name})
        context['teams'].append({
        'team_id':t.team_id,
        'nick':t.names[0],
        's_logo':'images/s_{}.png'.format(t.tricode)
        })
            
    for p in Player.objects.all().order_by('-jumps_jumped'):
        #filter for currently playing
        if len(p.prev_teams)>0 and p.is_jumper:
            team=p.prev_teams[-1]["teamId"]
            context['players_sel'].append({'nba_id':p.nba_id,'full_name':p.first_name+' '+p.last_name,'team_id':team})

    if 'playerddl1' in request.GET and 'playerddl2' in request.GET:
        player=Player.objects.get(nba_id=request.GET['playerddl1'])
        context['p1']=player.first_name+' '+player.last_name
        context['elos'].append({'full_name':context['p1'],'elo':'{:.0f}'.format(player.elo_score), 'jumps':player.jumps_jumped})
        
        player=Player.objects.get(nba_id=request.GET['playerddl2'])
        context['p2']=player.first_name+' '+player.last_name
        context['elos'].append({'full_name':context['p2'],'elo':'{:.0f}'.format(player.elo_score), 'jumps':player.jumps_jumped})
        
        context['prob']='{:.1f}'.format(compareRating(float(context['elos'][0]['elo']),float(context['elos'][1]['elo']))*100)

    
    return render(request, 'elo_compare.html', context=context)
