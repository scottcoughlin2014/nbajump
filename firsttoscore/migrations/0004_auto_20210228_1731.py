# Generated by Django 3.1.4 on 2021-02-28 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firsttoscore', '0003_teamtoscorefirstodds'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='odds',
            field=models.FloatField(default=0),
        ),
        migrations.DeleteModel(
            name='TeamToScoreFirstOdds',
        ),
    ]
