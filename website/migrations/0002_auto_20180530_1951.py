# Generated by Django 2.0 on 2018-05-31 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disbursement',
            name='date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='matter',
            name='invoice_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='service',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
