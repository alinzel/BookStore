# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_auto_20180123_0801'),
        ('users', '0002_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderBooks',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('count', models.IntegerField(default=1, verbose_name='商品数量')),
                ('price', models.DecimalField(max_digits=10, verbose_name='价格', decimal_places=2)),
                ('book', models.ForeignKey(to='books.Book', verbose_name='订单商品')),
            ],
            options={
                'db_table': 's_order_books',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('order_id', models.CharField(serialize=False, verbose_name='订单编号', primary_key=True, max_length=64)),
                ('total_count', models.IntegerField(default=1, verbose_name='商品总数')),
                ('total_price', models.DecimalField(max_digits=10, verbose_name='商品总价', decimal_places=2)),
                ('transit_price', models.DecimalField(max_digits=10, verbose_name='订单运费', decimal_places=2)),
                ('pay_method', models.SmallIntegerField(choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')], verbose_name='支付方式', default=1)),
                ('status', models.SmallIntegerField(choices=[(1, '待支付'), (2, '代发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')], verbose_name='订单状态', default=1)),
                ('trade_id', models.CharField(unique=True, null=True, verbose_name='支付编号', max_length=100, blank=True)),
                ('addr', models.ForeignKey(to='users.Address', verbose_name='收货地址')),
                ('passport', models.ForeignKey(to='users.PassPort', verbose_name='下单账户')),
            ],
            options={
                'db_table': 's_order_info',
            },
        ),
        migrations.AddField(
            model_name='orderbooks',
            name='order',
            field=models.ForeignKey(to='order.OrderInfo', verbose_name='所属订单'),
        ),
    ]
