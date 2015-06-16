# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Shopkeeper team, see AUTHORS.
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool

from company import Company
from shipment import ShipmentIn, ShipmentOut
from account import Move as AccountMove


def register():
    Pool.register(
        Company,
        ShipmentIn,
        ShipmentOut,
        AccountMove,
        module='shopkeeper', type_='model'
    )
