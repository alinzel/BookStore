# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(verbose_name='是否删除', default=False)),
                ('recipient_name', models.CharField(verbose_name='收件人姓名', max_length=20)),
                ('recipient_addr', models.CharField(verbose_name='收件人地址', max_length=256)),
                ('zip_code', models.CharField(verbose_name='邮政编码', max_length=6)),
                ('recipient_phone', models.CharField(verbose_name='联系电话', max_length=11)),
                ('is_default', models.BooleanField(verbose_name='是否默认', default=False)),
                ('passport', models.ForeignKey(verbose_name='账户', to='users.PassPort')),
            ],
            options={
                'db_table': 's_user_address',
            },
        ),
    ]
