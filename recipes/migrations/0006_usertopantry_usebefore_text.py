# Generated by Django 3.0.6 on 2020-06-10 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20200610_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertopantry',
            name='usebefore_text',
            field=models.CharField(choices=[('Use By', 'Use By'), ('Best Before', 'Best Before')], max_length=64, null=True),
        ),
    ]
