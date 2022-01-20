# Generated by Django 3.2.7 on 2022-01-03 17:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_cartitemtelegram_carttelegram'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertelegram',
            name='telegram_id',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
    ]