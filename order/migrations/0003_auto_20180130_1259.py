# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20180127_0202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='status',
            field=models.SmallIntegerField(default=1, verbose_name='订单状态', choices=[(0, '已付款'), (1, '待支付'), (2, '代发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')]),
        ),
    ]
