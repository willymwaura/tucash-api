# Generated by Django 4.2.3 on 2023-09-19 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_paybilltranscations_transaction_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paybilltranscations',
            old_name='transaction_id',
            new_name='OriginatorConversationID',
        ),
        migrations.RenameField(
            model_name='tilltranscations',
            old_name='transaction_id',
            new_name='OriginatorConversationID',
        ),
    ]
