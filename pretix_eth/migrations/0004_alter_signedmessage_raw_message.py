# Generated by Django 3.2.12 on 2022-07-08 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pretix_eth', '0003_signedmessage_transaction_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signedmessage',
            name='raw_message',
            field=models.TextField(),
        ),
    ]