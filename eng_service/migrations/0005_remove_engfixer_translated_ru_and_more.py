# Generated by Django 4.2.5 on 2023-10-26 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eng_service', '0004_rename_user_request_user_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='engfixer',
            name='translated_RU',
        ),
        migrations.AddField(
            model_name='engfixer',
            name='translated_fixed',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='engfixer',
            name='translated_input',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
