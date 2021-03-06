# Generated by Django 2.1.2 on 2019-04-16 10:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xtreembackend', '0011_auto_20190416_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='from_node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refersTo', to='xtreembackend.Node'),
        ),
        migrations.AlterField(
            model_name='link',
            name='to_node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referredFrom', to='xtreembackend.Node'),
        ),
    ]
