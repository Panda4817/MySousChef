# Generated by Django 3.0.6 on 2020-06-08 12:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertopantry',
            name='added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='usertopantry',
            name='bestbefore',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='usertopantry',
            name='opened',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='usertopantry',
            name='use_within',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='usertopantry',
            name='usebefore',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.RemoveField(
            model_name='usertopantry',
            name='pantry_item',
        ),
        migrations.AddField(
            model_name='usertopantry',
            name='pantry_item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='recipes.Pantry'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usertopantry',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
