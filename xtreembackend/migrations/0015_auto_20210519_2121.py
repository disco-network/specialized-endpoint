# Generated by Django 2.1.2 on 2021-05-19 21:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xtreembackend', '0014_auto_20210519_2117'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='link',
            unique_together={('to_node', 'from_node')},
        ),
    ]