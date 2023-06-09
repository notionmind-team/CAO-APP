# Generated by Django 3.0.5 on 2020-04-21 15:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_subcategory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('publish', models.BooleanField(default=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('updatedAt', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Family',
                'verbose_name_plural': 'Families',
            },
        ),
    ]
