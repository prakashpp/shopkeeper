# -*- coding: utf-8 -*-
"""
    account.py

    :copyright: (c) 2014 by Shopkeeper team, see AUTHORS.
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta

__metaclass__ = PoolMeta
__all__ = ['Move']


class Move:
    __name__ = 'account.move'

    @classmethod
    def _get_origin(cls):
        res = super(Move, cls)._get_origin()
        res.append('stock.move')

        return res
