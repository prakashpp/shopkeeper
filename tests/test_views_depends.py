# -*- coding: utf-8 -*-
"""
    tests/test_views_depends.py

    :copyright: (c) 2014 by Shopkeeper team, see AUTHORS.
    :license: BSD, see LICENSE for more details
"""


class TestViewDepends:

    def test_views(self):
        "Test all tryton views"

        from trytond.tests.test_tryton import test_view
        test_view('shopkeeper')

    def test_depends(self):
        "Test missing depends on fields"

        from trytond.tests.test_tryton import test_depends
        test_depends()
