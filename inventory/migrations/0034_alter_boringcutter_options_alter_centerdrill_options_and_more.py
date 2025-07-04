# Generated by Django 4.2.5 on 2023-10-30 22:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('inventory', '0033_screw'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='boringcutter',
            options={'verbose_name_plural': 'Boring cutters'},
        ),
        migrations.AlterModelOptions(
            name='centerdrill',
            options={'verbose_name_plural': 'Center drills'},
        ),
        migrations.AlterModelOptions(
            name='chamfermill',
            options={'verbose_name_plural': 'Chamfer mills'},
        ),
        migrations.AlterModelOptions(
            name='circularsaw',
            options={'ordering': ['-thickness', '-diameter'], 'verbose_name_plural': 'Circular saws'},
        ),
        migrations.AlterModelOptions(
            name='collet',
            options={'ordering': ['type', 'diameter'], 'verbose_name_plural': 'Collets'},
        ),
        migrations.AlterModelOptions(
            name='drillinginsert',
            options={'verbose_name_plural': 'Drilling inserts'},
        ),
        migrations.AlterModelOptions(
            name='endmill',
            options={'verbose_name_plural': 'End mills'},
        ),
        migrations.AlterModelOptions(
            name='facemill',
            options={'verbose_name_plural': 'Face mills'},
        ),
        migrations.AlterModelOptions(
            name='generalcutter',
            options={'verbose_name_plural': 'General cutters'},
        ),
        migrations.AlterModelOptions(
            name='groovingexternalcutter',
            options={'verbose_name_plural': 'Grooving external cutters'},
        ),
        migrations.AlterModelOptions(
            name='groovinginsert',
            options={'ordering': ['width'], 'verbose_name_plural': 'Grooving inserts'},
        ),
        migrations.AlterModelOptions(
            name='groovinginternalcutter',
            options={'verbose_name_plural': 'Grooving internal cutters'},
        ),
        migrations.AlterModelOptions(
            name='lollipopmill',
            options={'ordering': ['-diameter', '-neck_diameter'], 'verbose_name_plural': 'Lollipop mills'},
        ),
        migrations.AlterModelOptions(
            name='measuringequipment',
            options={'verbose_name_plural': 'Measuring equipments'},
        ),
        migrations.AlterModelOptions(
            name='millingholder',
            options={'ordering': ['diameter', 'name'], 'verbose_name_plural': 'Milling holders'},
        ),
        migrations.AlterModelOptions(
            name='millinginsert',
            options={'verbose_name_plural': 'Milling inserts'},
        ),
        migrations.AlterModelOptions(
            name='radiusmill',
            options={'ordering': ['-radius', '-flute_length'], 'verbose_name_plural': 'Radius mills'},
        ),
        migrations.AlterModelOptions(
            name='solidboringcutter',
            options={'verbose_name_plural': 'Boring cutters'},
        ),
        migrations.AlterModelOptions(
            name='solidgroovingcutter',
            options={'verbose_name_plural': 'Solid grooving cutters'},
        ),
        migrations.AlterModelOptions(
            name='solidthreadcutter',
            options={'verbose_name_plural': 'Solid thread cutters'},
        ),
        migrations.AlterModelOptions(
            name='spotdrill',
            options={'verbose_name_plural': 'Spot drills'},
        ),
        migrations.AlterModelOptions(
            name='tap',
            options={'verbose_name_plural': 'Taps'},
        ),
        migrations.AlterModelOptions(
            name='threadexternalcutter',
            options={'verbose_name_plural': 'Thread external cutters'},
        ),
        migrations.AlterModelOptions(
            name='threadinternalcutter',
            options={'verbose_name_plural': 'Thread internal cutters'},
        ),
        migrations.AlterModelOptions(
            name='threadmill',
            options={'verbose_name_plural': 'Thread mills'},
        ),
        migrations.AlterModelOptions(
            name='tslotmill',
            options={'ordering': ['-thickness', '-diameter'], 'verbose_name_plural': 'T-slot mills'},
        ),
        migrations.AlterModelOptions(
            name='u_drill',
            options={'verbose_name_plural': 'U-drills'},
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('order_date', models.DateField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Received', 'Received'), ('Cancelled', 'Cancelled'), ('Ordered', 'Ordered'), ('Unknown', 'Unknown')], default='Pending', max_length=50)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name_plural': 'Orders',
                'ordering': ['-order_date'],
            },
        ),
    ]
