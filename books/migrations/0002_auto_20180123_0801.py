# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'verbose_name_plural': '书籍信息', 'verbose_name': '书籍信息'},
        ),
        migrations.AddField(
            model_name='book',
            name='sales',
            field=models.IntegerField(default=0, verbose_name='商品销量'),
        ),
    ]
