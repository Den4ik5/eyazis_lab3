# Generated by Django 3.1.2 on 2020-10-23 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parse_text', '0003_document_theme'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='args',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
