# Generated by Django 2.0 on 2018-05-31 02:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Disbursement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('tax_choice', models.CharField(choices=[('Taxable', 'Taxable'), ('Non-Taxable', 'Non-Taxable')], max_length=20, verbose_name='Taxable/Non-Taxable')),
            ],
        ),
        migrations.CreateModel(
            name='Lawyer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Matter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_number', models.CharField(max_length=50)),
                ('invoice_date', models.DateTimeField(auto_now_add=True)),
                ('invoice_number', models.CharField(max_length=50)),
                ('summary', models.CharField(max_length=255)),
                ('fee_choice', models.CharField(choices=[('Fixed', 'Fixed'), ('Hourly', 'Hourly')], max_length=20, verbose_name='Fixed fee or hourly?')),
                ('trust', models.DecimalField(decimal_places=2, max_digits=6)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Client')),
                ('lawyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Lawyer')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=255)),
                ('hours', models.IntegerField(blank=True, default=0)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('lawyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Lawyer')),
                ('matter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Matter')),
            ],
        ),
        migrations.AddField(
            model_name='disbursement',
            name='matter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Matter'),
        ),
    ]
