from django.core.management.base import BaseCommand, CommandError
from firsttoscore.models import Player
from firsttoscore.management.commands.update_stats import compareRating


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("player1",help="Team name")
        parser.add_argument("player2",help="Team name")


    def handle(self, *args, **options):

        elos=[]
        for _p in ["player1","player2"]:
            
            p=Player.objects.filter(last_name=options[_p])

            if len(p)==0:
                print('{} not found.'.format(options[_p]))
            elif len(p)>1:
                print('Many players named {} found.'.format(options[_p]))
                for i,_j in enumerate(p):
                    print('{} - {} {}'.format(i+1,_j.first_name,_j.last_name))
                f=input('Select the desired index: ')
                elos.append(p[int(f)-1])
                
            else:
                elos.append(p[0])

        print('\n')
        print('{} {} - elo: {:.2f} ({} jumps)'.format(elos[0].first_name,elos[0].last_name,elos[0].elo_score,elos[0].jumps_jumped))
        print('{} {} - elo: {:.2f} ({} jumps)'.format(elos[1].first_name,elos[1].last_name,elos[1].elo_score,elos[1].jumps_jumped))

        prob=compareRating(elos[0].elo_score,elos[1].elo_score)*100

        print('{} has {:.2f}% of probability of beating {}.'.format(elos[0].last_name,prob,elos[1].last_name))
        print('\n')
