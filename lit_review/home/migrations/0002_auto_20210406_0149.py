# Generated by Django 3.1.7 on 2021-04-05 23:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='description',
            field=models.CharField(blank=True, max_length=2048),
        ),
        migrations.AddField(
            model_name='ticket',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='title',
            field=models.CharField(default=' ', max_length=128),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='time_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]