# Generated by Django 3.2.16 on 2023-01-28 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0020_usertorecipe_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipes',
            name='health_score',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
