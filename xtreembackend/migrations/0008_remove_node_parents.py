# Generated by Django 2.1.2 on 2019-04-13 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xtreembackend', '0007_auto_20190413_1644'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='node',
            name='parents',
        ),
    ]
