# Generated by Django 2.1.dev20180316013315 on 2018-03-16 10:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Insider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('relation', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='InsiderTradeEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('transaction_type', models.CharField(max_length=200)),
                ('owner_type', models.CharField(max_length=200)),
                ('shares_traded', models.IntegerField(default=0)),
                ('shares_held', models.IntegerField(default=0)),
                ('last_price', models.FloatField(default=0.0)),
                ('insider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shares.Insider')),
            ],
        ),
        migrations.CreateModel(
            name='Share',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TradeEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('volume', models.IntegerField(default=0)),
                ('open', models.FloatField(default=0.0)),
                ('high', models.FloatField(default=0.0)),
                ('low', models.FloatField(default=0.0)),
                ('close', models.FloatField(default=0.0)),
                ('share', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shares.Share')),
            ],
        ),
        migrations.AddField(
            model_name='insidertradeevent',
            name='share',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shares.Share'),
        ),
    ]
