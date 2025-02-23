# Generated by Django 3.2.12 on 2024-10-18 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_auto_20241018_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='address_area',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_profiles', to='shop.area'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='address_city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_profiles', to='shop.city'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='address_district',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_profiles', to='shop.district'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='address_neighborhood',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_profiles', to='shop.neighborhood'),
        ),
    ]
