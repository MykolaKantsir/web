# Generated by Django 4.2.5 on 2024-10-05 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0014_monitoroperation_machine_is_test_machine_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='monitorOperation',
            new_name='Monitor_operation',
        ),
        migrations.RenameField(
            model_name='monitor_operation',
            old_name='monito_operation_id',
            new_name='monitor_operation_id',
        ),
    ]
