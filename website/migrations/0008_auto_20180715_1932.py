# Generated by Django 2.0 on 2018-07-16 02:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_auto_20180715_1914'),
    ]

    operations = [
        migrations.RenameField(
            model_name='matter',
            old_name='invoice_number',
            new_name='matter_number',
        ),
    ]