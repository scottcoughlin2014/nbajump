#!/usr/bin/env python
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from firsttoscore.models import Player

class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Applying patch')
       
        TODAY_UTC = timezone.now()
        jumpers=[203500,1628389,200746,1628386,203507,1628384,1629028,1628963,203382,1629647,202687,1628396,1628418,203991,1628976,1626161,1629634,1628381,203076,202334,203476,203083,201142,203954,1629655,201188,203497,201933,1629637,1626158,201143,2730,201586,1629640,203999,201599,202683,203458,1626172,201572,201577,201580,203994,203486,1627751,204001,203939,1629675,1629011,1629676,1627734,203471,1629012,1628464,202684,1629308,1626157,1626167,202685,202696,1626174,203469,1627826,1630173,202326,1630214,1630164,203084,2199,203473,2200,101162,101161,201567,1627748,1626175,200794,202389,203457,203512,2585,202355,1626177,1626171,203210,1627863,1627732]
       
        for j in jumpers:
            if Player.objects.filter(nba_id=j).exists():
                p=Player.objects.get(nba_id=j)
                p.is_jumper=1
                p.last_update = TODAY_UTC
                p.save()
                print('Player {0} (id: {1}) set to be a jumper.'.format(p.last_name,j))

        if Player.objects.filter(nba_id=2403).exists():
            p=Player.objects.get(nba_id=2403)
            p.last_name=p.first_name
            p.last_update = TODAY_UTC
            p.save()
            print('Put {0} as last_name.'.format(p.first_name))

        if not Player.objects.filter(nba_id=203186).exists():
            Player.objects.create(nba_id = 203186, first_name = 'Willie', last_name = 'Reed', team_id = 1610612746, prev_teams = [{"teamId": "1610612746", "seasonStart": "2017", "seasonEnd": "2017"}], last_update = TODAY_UTC)
            print('Added Willie Reed (id: 203186)')

        if not Player.objects.filter(nba_id=203477).exists():
            Player.objects.create(nba_id = 203477, first_name = 'Isaiah', last_name = 'Canaan', team_id = 1610612756, prev_teams = [{"teamId": "1610612756", "seasonStart": "2018", "seasonEnd": "2018"}], last_update = TODAY_UTC)
            print('Added Isaiah Canaan (id: 203477)')

        if not Player.objects.filter(nba_id=1628455).exists():
            Player.objects.create(nba_id = 1628455, first_name = 'Mike', last_name = 'James', team_id = 1610612756, prev_teams = [{"teamId": "1610612756", "seasonStart": "2017", "seasonEnd": "2017"}], last_update = TODAY_UTC)
            print('Added Mike James (id: 1628455)')

        if not Player.objects.filter(nba_id=201956).exists():
            Player.objects.create(nba_id = 201956, first_name = 'Omri', last_name = 'Casspi', team_id = 1610612744, prev_teams = [{"teamId": "1610612744", "seasonStart": "2017", "seasonEnd": "2017"}], last_update = TODAY_UTC)
            print('Added Omri Casspi (id: 201956)')

        if not Player.objects.filter(nba_id=203966).exists():
            Player.objects.create(nba_id = 203966, first_name = 'Jamil', last_name = 'Wilson', team_id = 1610612746, prev_teams = [{"teamId": "1610612746", "seasonStart": "2017", "seasonEnd": "2017"}], last_update = TODAY_UTC)
            print('Added Jamil Wilson (id: 203966)')


