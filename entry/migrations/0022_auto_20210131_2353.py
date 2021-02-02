# Generated by Django 3.1.1 on 2021-01-31 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entry', '0021_auto_20210130_2321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visitor',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='visitor',
            name='photo_id',
        ),
        migrations.RemoveField(
            model_name='visitor',
            name='photo_id_number',
        ),
        migrations.AddField(
            model_name='visitor',
            name='actual_visitors',
            field=models.IntegerField(blank=True, null=True, verbose_name='Actual No. of Visitors'),
        ),
        migrations.AddField(
            model_name='visitorsdetail',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='media/photo', verbose_name='Photo of the Visitor'),
        ),
        migrations.AddField(
            model_name='visitorsdetail',
            name='photo_id',
            field=models.ImageField(blank=True, null=True, upload_to='media/photo_id', verbose_name='Photo Id'),
        ),
        migrations.AddField(
            model_name='visitorsdetail',
            name='photo_id_number',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Photo Id Number'),
        ),
    ]
