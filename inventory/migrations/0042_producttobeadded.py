# Generated by Django 4.2.5 on 2023-11-29 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0041_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductToBeAdded',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode', models.CharField(max_length=255, unique=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
