# Generated by Django 3.0.5 on 2020-04-22 06:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_item_moq'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='item',
        ),
        migrations.DeleteModel(
            name='Sales',
        ),
        migrations.DeleteModel(
            name='Stock',
        ),
    ]