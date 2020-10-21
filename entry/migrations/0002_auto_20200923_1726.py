# Generated by Django 3.1.1 on 2020-09-23 11:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entry', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='mobile',
            field=models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10, 'Enter a 10 digit mobile number'), django.core.validators.MaxLengthValidator(10)]),
        ),
    ]