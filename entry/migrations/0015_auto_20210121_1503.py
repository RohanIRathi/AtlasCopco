# Generated by Django 3.1.1 on 2021-01-21 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entry', '0014_auto_20201203_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitor',
            name='in_time',
            field=models.DateTimeField(blank=True, default='21/01/2021 03:03 PM', null=True, verbose_name='Visit In time'),
        ),
    ]