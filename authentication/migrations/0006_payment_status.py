# Generated by Django 4.2.1 on 2023-10-14 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_payment_payment_id_alter_booking_user_delete_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(default='pending', max_length=50),
        ),
    ]
