# Generated by Django 3.0.6 on 2020-06-10 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20200608_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertopantry',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddConstraint(
            model_name='usertopantry',
            constraint=models.CheckConstraint(check=models.Q(quantity__gt=0), name='quantity_gt_0'),
        ),
    ]
