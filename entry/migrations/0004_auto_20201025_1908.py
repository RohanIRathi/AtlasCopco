# Generated by Django 3.1.1 on 2020-10-25 13:38

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entry', '0003_user_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10, 'Enter a 10 digit mobile number'), django.core.validators.MaxLengthValidator(10)])),
                ('pic', models.ImageField(upload_to='media')),
                ('admin', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='visitor',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='entry.employee'),
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]