# Generated by Django 3.1.4 on 2021-02-28 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firsttoscore', '0005_auto_20210228_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='fd_id',
            field=models.FloatField(default=0),
        ),
    ]
