# Generated by Django 2.1.5 on 2019-03-25 12:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Danmu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('time', models.DateTimeField()),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='MicroProgram.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='Organizer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('open_id', models.IntegerField(primary_key=True, serialize=False)),
                ('nick_name', models.CharField(max_length=64)),
                ('avatar', models.URLField()),
                ('gender', models.SmallIntegerField()),
                ('country', models.CharField(max_length=64)),
                ('province', models.CharField(max_length=64)),
                ('city', models.CharField(max_length=64)),
                ('language', models.CharField(max_length=16)),
            ],
        ),
        migrations.AddField(
            model_name='danmu',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='MicroProgram.Participant'),
        ),
        migrations.AddField(
            model_name='activity',
            name='belong',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='MicroProgram.Organizer'),
        ),
        migrations.AddField(
            model_name='activity',
            name='participants',
            field=models.ManyToManyField(to='MicroProgram.Participant'),
        ),
    ]
