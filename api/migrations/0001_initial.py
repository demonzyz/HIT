# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('desc', models.CharField(max_length=50, null=True)),
                ('status', models.SmallIntegerField(choices=[(0, b'run'), (1, b'skip')])),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.FloatField(unique=True)),
                ('status', models.IntegerField(null=True, choices=[(0, b'running'), (1, b'finish')])),
                ('report', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('desc', models.CharField(max_length=50, null=True)),
                ('order', models.IntegerField(default=1)),
                ('check', models.CharField(max_length=500, null=True)),
                ('headers', models.CharField(max_length=500, null=True)),
                ('data', models.CharField(max_length=500, null=True)),
                ('case', models.ForeignKey(to='api.Case')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('desc', models.CharField(max_length=50, null=True)),
                ('case', models.ManyToManyField(to='api.Case')),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('desc', models.CharField(max_length=50, null=True)),
                ('url', models.URLField()),
                ('method', models.SmallIntegerField(choices=[(0, b'GET'), (1, b'POST')])),
                ('headers', models.CharField(max_length=500, null=True)),
                ('data', models.CharField(max_length=500, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='step',
            name='template',
            field=models.ForeignKey(to='api.Template'),
        ),
        migrations.AddField(
            model_name='history',
            name='task',
            field=models.ForeignKey(to='api.Task'),
        ),
    ]
