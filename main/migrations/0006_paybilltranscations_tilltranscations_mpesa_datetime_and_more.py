# Generated by Django 4.2.3 on 2023-09-16 17:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_transactions_receiver'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaybillTranscations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paybill', models.IntegerField(default=0)),
                ('account_number', models.CharField(default=3)),
                ('amount', models.IntegerField(default=0)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TillTranscations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('till_number', models.IntegerField(default=0)),
                ('amount', models.IntegerField(default=0)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='mpesa',
            name='datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='mpesa',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
