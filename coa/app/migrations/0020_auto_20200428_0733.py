# Generated by Django 3.0.5 on 2020-04-28 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_auto_20200428_0726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orederitem',
            name='moq',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='orederitem',
            name='on_hand_quanty',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='orederitem',
            name='order_quantity',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='orederitem',
            name='total_quantity',
            field=models.IntegerField(),
        ),
    ]
