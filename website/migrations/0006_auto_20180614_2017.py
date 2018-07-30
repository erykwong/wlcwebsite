# Generated by Django 2.0 on 2018-06-15 03:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_auto_20180606_2011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='matter',
            name='discount',
        ),
        migrations.AddField(
            model_name='discount',
            name='matter',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='website.Matter'),
            preserve_default=False,
        ),
    ]
