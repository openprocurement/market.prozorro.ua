# Generated by Django 2.2.7 on 2019-11-13 12:24

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Criteria',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, null=True)),
                ('name_eng', models.CharField(max_length=255, null=True)),
                ('min_value', models.CharField(max_length=50, null=True)),
                ('max_value', models.CharField(max_length=50, null=True)),
                ('unit_code', models.CharField(max_length=5)),
                ('unit_name', models.CharField(max_length=50)),
                ('data_type', models.CharField(choices=[('string', 'string'), ('boolean', 'boolean'), ('integer', 'integer'), ('number', 'number')], max_length=10)),
                ('classification_id', models.CharField(max_length=10)),
                ('additional_classification_id', models.CharField(max_length=10, null=True)),
                ('classification_description', models.CharField(max_length=255)),
                ('additional_classification_description', models.CharField(max_length=255, null=True)),
                ('classification_scheme', models.CharField(max_length=10)),
                ('additional_classification_scheme', models.CharField(max_length=10, null=True)),
                ('date_modified', models.DateField(auto_now=True)),
                ('archive', models.BooleanField(default=False)),
            ],
        ),
    ]
