# Generated by Django 4.2.3 on 2023-09-27 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_rename_mpesa_mpesadeposits_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paybilltranscations',
            name='user_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tilltranscations',
            name='user_id',
            field=models.IntegerField(default=0),
        ),
    ]
