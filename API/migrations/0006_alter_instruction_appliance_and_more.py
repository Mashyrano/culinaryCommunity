# Generated by Django 5.1.4 on 2025-01-16 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0005_instruction_step'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instruction',
            name='appliance',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='instruction',
            name='position',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='instruction',
            name='temperatureF',
            field=models.IntegerField(null=True),
        ),
    ]
