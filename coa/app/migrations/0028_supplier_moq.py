# Generated by Django 3.0.5 on 2020-05-14 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_auto_20200512_2058'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='moq',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
