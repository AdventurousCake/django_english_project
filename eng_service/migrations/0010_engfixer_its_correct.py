# Generated by Django 4.2.5 on 2023-12-13 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eng_service', '0009_alter_tag_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='engfixer',
            name='its_correct',
            field=models.BooleanField(default=None, null=True),
        ),
    ]
