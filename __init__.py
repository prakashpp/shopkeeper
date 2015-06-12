# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Shopkeeper team, see AUTHORS.
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool


def register():
    Pool.register(
        module='shopkeeper', type_='model'
    )
