# Generated by Django 3.0.5 on 2020-04-29 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_auto_20200429_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='sku',
            field=models.CharField(max_length=255),
        ),
    ]