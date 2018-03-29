# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderbooks',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间', default=datetime.datetime(2018, 1, 27, 2, 1, 51, 108571, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderbooks',
            name='is_delete',
            field=models.BooleanField(verbose_name='是否删除', default=False),
        ),
        migrations.AddField(
            model_name='orderbooks',
            name='update_at',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间', default=datetime.datetime(2018, 1, 27, 2, 2, 11, 331548, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
