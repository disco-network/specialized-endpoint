# Generated by Django 2.1.2 on 2019-04-13 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xtreembackend', '0007_auto_20190413_1138'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
