# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-09 18:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fit', '0004_auto_20170509_1800'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tags',
            new_name='Tag',
        ),
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(upload_to='images/'),
        ),
    ]
