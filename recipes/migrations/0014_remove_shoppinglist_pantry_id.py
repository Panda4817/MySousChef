# Generated by Django 3.0.6 on 2020-06-15 21:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0013_shoppinglist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppinglist',
            name='pantry_id',
        ),
    ]
