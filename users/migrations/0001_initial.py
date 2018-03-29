# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PassPort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('create_at', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_at', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='是否删除', default=False)),
                ('username', models.CharField(verbose_name='用户名', max_length=20)),
                ('password', models.CharField(verbose_name='密码', max_length=40)),
                ('email', models.EmailField(verbose_name='邮箱', max_length=254)),
                ('is_active', models.BooleanField(verbose_name='激活状态', default=False)),
            ],
            options={
                'db_table': 's_user_account',
            },
        ),
    ]
