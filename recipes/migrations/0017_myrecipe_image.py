# Generated by Django 3.0.7 on 2020-06-18 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_usertomyrecipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='myrecipe',
            name='image',
            field=models.CharField(default='salad.png', max_length=64),
        ),
    ]
