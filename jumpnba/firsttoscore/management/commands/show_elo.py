import sys,os
from django.core.management.base import BaseCommand, CommandError
from players.models import Player
from operator import itemgetter


class Command(BaseCommand):

    def handle(self, *args, **options):
        ss=[]
        for p in Player.objects.filter(is_jumper=1):
            ss.append([p.first_name,p.last_name,p.elo_score,p.jumps_jumped])

        for el in sorted(ss,reverse=True,key=itemgetter(2)):
            print('{: <24} {:.2f} ({:>3} jumps)'.format(el[0]+' '+el[1],el[2],el[3]))
