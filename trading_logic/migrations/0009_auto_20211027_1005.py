# Generated by Django 3.2.8 on 2021-10-27 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trading_logic', '0008_alter_watchlist_items'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='item',
        ),
        migrations.AddField(
            model_name='offer',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='trading_logic.item'),
        ),
    ]
