# Generated by Django 4.2.5 on 2024-02-13 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0044_alter_ballmill_manufacturer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ballmill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='boringcutter',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='centerdrill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='chamfermill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='circularsaw',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='collet',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='drill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='drillinginsert',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='endmill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='equipmentmilling',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='equipmentturning',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='facemill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='generalcutter',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='groovingexternalcutter',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='groovinginsert',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='groovinginternalcutter',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='key',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='lollipopmill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='measuringequipment',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='millingbody',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='millingholder',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='millinginsert',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='postmachining',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='radiusmill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='reamer',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='screw',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='screwdriver',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='shim',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='solidboringcutter',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='solidgroovingcutter',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='solidthreadcutter',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='spotdrill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='tap',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='threadexternalcutter',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='threadinsert',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='threadinternalcutter',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='threadmill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='tslotmill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='turninginsert',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='u_drill',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='workholding',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='wrench',
            name='manufacturer',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('ceratizit', 'Ceratizit'), ('guehring', 'Guehring'), ('hoffmann', 'Hoffmann'), ('tungaloy', 'Tungaloy'), ('sandvik', 'Sandvik'), ('walter', 'Walter'), ('duemmel', 'Duemmel'), ('phorn', 'Phorn'), ('skene järn', 'Skenejarn'), ('precision detaljer', 'Precision Detaljer')], default='Unknown', max_length=50),
        ),
        migrations.CreateModel(
            name='WeekOrders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('week', models.IntegerField()),
                ('orders', models.ManyToManyField(related_name='week_orders', to='inventory.order')),
            ],
            options={
                'unique_together': {('year', 'week')},
            },
        ),
    ]
