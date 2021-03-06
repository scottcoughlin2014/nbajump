# Generated by Django 3.1.7 on 2021-02-20 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.IntegerField()),
                ('game_id', models.CharField(max_length=15)),
                ('game_utc', models.DateTimeField()),
                ('game_date', models.CharField(max_length=8)),
                ('game_time', models.CharField(max_length=8)),
                ('stage', models.IntegerField()),
                ('tricode', models.CharField(max_length=6)),
                ('h_team', models.CharField(max_length=15)),
                ('a_team', models.CharField(max_length=15)),
                ('jumpers', models.JSONField()),
                ('jump_win', models.IntegerField()),
                ('team_first_score', models.IntegerField()),
                ('player_first_score', models.IntegerField()),
                ('all_first_scorers', models.JSONField()),
                ('all_first_shooters', models.JSONField()),
                ('last_update', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nba_id', models.IntegerField()),
                ('fd_id', models.IntegerField(null=1)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('team_id', models.CharField(max_length=100)),
                ('prev_teams', models.JSONField()),
                ('is_jumper', models.BooleanField(default=0)),
                ('jumps_jumped', models.IntegerField(default=0)),
                ('jumps_won', models.IntegerField(default=0)),
                ('elo_score', models.FloatField(default=1500)),
                ('last_update', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.IntegerField()),
                ('full_name', models.CharField(max_length=100)),
                ('tricode', models.CharField(max_length=3)),
                ('names', models.JSONField()),
                ('stats', models.JSONField()),
                ('last_update', models.DateTimeField()),
            ],
        ),
    ]
