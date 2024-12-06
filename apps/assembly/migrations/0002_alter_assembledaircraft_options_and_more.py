# Generated by Django 4.2 on 2024-12-06 03:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0001_initial'),
        ('teams', '0001_initial'),
        ('assembly', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assembledaircraft',
            options={'ordering': ['-created_at'], 'verbose_name': 'Assembled Aircraft', 'verbose_name_plural': 'Assembled Aircraft'},
        ),
        migrations.RenameField(
            model_name='assembledaircraft',
            old_name='assembly_date',
            new_name='created_at',
        ),
        migrations.RemoveField(
            model_name='assembledaircraft',
            name='avionics',
        ),
        migrations.RemoveField(
            model_name='assembledaircraft',
            name='fuselage',
        ),
        migrations.RemoveField(
            model_name='assembledaircraft',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='assembledaircraft',
            name='serial_number',
        ),
        migrations.RemoveField(
            model_name='assembledaircraft',
            name='tail',
        ),
        migrations.RemoveField(
            model_name='assembledaircraft',
            name='wing',
        ),
        migrations.AddField(
            model_name='assembledaircraft',
            name='parts',
            field=models.ManyToManyField(related_name='assembled_in', to='parts.part'),
        ),
        migrations.AddField(
            model_name='assembledaircraft',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='assembledaircraft',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='assembledaircraft',
            name='assembly_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assembled_aircraft', to='teams.team'),
        ),
    ]
