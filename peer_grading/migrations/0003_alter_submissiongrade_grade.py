# Generated by Django 4.2.2 on 2023-07-19 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peer_grading', '0002_submissiongrade_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissiongrade',
            name='grade',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
