# Generated by Django 2.2.7 on 2020-02-10 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_profile_access_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='unit_name',
            field=models.CharField(max_length=100),
        ),
    ]
