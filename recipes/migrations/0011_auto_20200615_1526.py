# Generated by Django 3.0.6 on 2020-06-15 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_recipes_wine_pairing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipes',
            name='credit',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
