# Generated by Django 3.2.9 on 2022-01-01 11:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_usertelegram'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertelegram',
            name='otp',
            field=models.CharField(default=django.utils.timezone.now, max_length=30),
            preserve_default=False,
        ),
    ]
