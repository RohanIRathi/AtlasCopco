# Generated by Django 3.1.1 on 2020-11-04 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entry', '0011_auto_20201027_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitor',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='media/photo', verbose_name='Photo of the Visitor'),
        ),
    ]