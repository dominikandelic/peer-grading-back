# Generated by Django 4.2.3 on 2023-07-20 22:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('peer_grading', '0003_alter_submissiongrade_grade'),
    ]

    operations = [
        migrations.CreateModel(
            name='GradingResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.IntegerField()),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='peer_grading.submission')),
            ],
        ),
    ]
