# Generated by Django 4.2.5 on 2023-09-23 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_alter_endmill_neck_diameter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endmill',
            name='coating',
            field=models.CharField(default='Undefined', max_length=50),
        ),
    ]
