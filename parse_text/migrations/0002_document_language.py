# Generated by Django 3.1.2 on 2020-10-22 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parse_text', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='language',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
    ]
