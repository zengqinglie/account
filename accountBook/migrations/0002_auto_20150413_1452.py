# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accountBook', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cost',
            field=models.DecimalField(max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sumcost',
            name='sum_cost',
            field=models.DecimalField(max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
    ]
