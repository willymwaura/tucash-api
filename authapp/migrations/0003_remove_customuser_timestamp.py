# Generated by Django 4.2.3 on 2023-09-12 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0002_alter_customuser_timestamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='timestamp',
        ),
    ]
