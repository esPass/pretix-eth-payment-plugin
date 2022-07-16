# Generated by Django 3.2.12 on 2022-07-16 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pretix_eth', '0005_alter_signedmessage_chain_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='signedmessage',
            name='created_at',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='signedmessage',
            name='invalid',
            field=models.BooleanField(default=False),
        ),
    ]
