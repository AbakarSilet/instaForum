# Generated by Django 5.1.3 on 2025-04-02 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_post_is_closed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='is_closed',
        ),
        migrations.AddField(
            model_name='thread',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
    ]
