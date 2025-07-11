# Generated by Django 4.2.5 on 2024-10-05 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0013_job_is_ready_to_finish'),
    ]

    operations = [
        migrations.CreateModel(
            name='monitorOperation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monito_operation_id', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=50)),
                ('quantity', models.IntegerField(default=0)),
                ('material', models.CharField(max_length=50)),
                ('report_number', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='machine',
            name='is_test_machine',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='machine',
            name='monitor_arp_id',
            field=models.IntegerField(default=0),
        ),
    ]
