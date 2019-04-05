# Generated by Django 2.1.8 on 2019-04-03 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tom_observations', '0002_auto_20190306_2343'),
        ('tom_targets', '0005_auto_20190214_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObservationTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template', models.BooleanField(default=False)),
                ('observation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tom_observations.ObservationRecord')),
            ],
        ),
        migrations.CreateModel(
            name='TimeLapse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('timelapse_mpeg', models.FileField(blank=True, null=True, upload_to='')),
                ('timelapse_webm', models.FileField(blank=True, null=True, upload_to='')),
                ('num_observations', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=False)),
                ('target', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tom_targets.Target')),
            ],
        ),
    ]