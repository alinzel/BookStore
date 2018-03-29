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
            name='Comments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_at', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_at', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('disabled', models.BooleanField(default=False, verbose_name='禁用评论')),
                ('content', models.CharField(verbose_name='评论内容', max_length=1000)),
                ('book', models.ForeignKey(to='books.Book', verbose_name='书籍ID')),
                ('user', models.ForeignKey(to='users.PassPort', verbose_name='用户ID')),
            ],
            options={
                'db_table': 's_comment_table',
            },
        ),
    ]
