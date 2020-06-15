# Generated by Django 3.0.6 on 2020-06-13 17:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_usertopantry_usebefore_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_id', models.PositiveIntegerField()),
                ('title', models.CharField(max_length=200)),
                ('image', models.URLField()),
                ('serves', models.PositiveIntegerField()),
                ('time', models.PositiveIntegerField()),
                ('source_url', models.URLField()),
                ('credit', models.CharField(max_length=200)),
                ('health_score', models.DecimalField(decimal_places=2, max_digits=4)),
                ('popularity', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='RecipeIngredients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=3, max_digits=7)),
                ('unit', models.CharField(max_length=64)),
                ('meta', models.CharField(max_length=200)),
                ('recipe_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipes')),
            ],
        ),
    ]
