# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-11 11:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('wcore', '0003_auto_20170908_1401'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='runner',
            options={'ordering': ['name'], 'verbose_name': 'Execution environment', 'verbose_name_plural': 'Executions'},
        ),
        migrations.AlterModelManagers(
            name='booleanparam',
            managers=[
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='decimalparam',
            managers=[
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='fileinput',
            managers=[
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='integerparam',
            managers=[
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='listparam',
            managers=[
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='textparam',
            managers=[
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='runner',
            name='binary_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wcore.ServiceBinaryFile'),
        ),
        migrations.AddField(
            model_name='service',
            name='binary_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wcore.ServiceBinaryFile'),
        ),
        migrations.AddField(
            model_name='submission',
            name='binary_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wcore.ServiceBinaryFile'),
        ),
    ]