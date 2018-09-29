# Generated by Django 2.1.1 on 2018-09-29 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xtreembackend', '0002_auto_20180929_2232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='node',
            name='children',
        ),
        migrations.AlterField(
            model_name='node',
            name='parents',
            field=models.ManyToManyField(related_name='children', to='xtreembackend.Node'),
        ),
    ]
