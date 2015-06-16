# -*- coding: utf-8 -*-
"""
    company.py

    :copyright: (c) 2014 by Shopkeeper team, see AUTHORS.
    :license: BSD, see LICENSE for more details.
"""
import datetime

from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.transaction import Transaction
from validate_email import validate_email
from dateutil.relativedelta import relativedelta

__metaclass__ = PoolMeta
__all__ = ['Company']


class Company:
    __name__ = "company.company"

    customer = fields.Many2One(
        "party.party", "Customer", required=True, select=True
    )
    supplier = fields.Many2One(
        "party.party", "Supplier", required=True, select=True
    )

    @classmethod
    def __setup__(cls):
        super(Company, cls).__setup__()

        cls._error_messages.update({
            'invalid_email_address': 'Email address is invalid'
        })

    def _create_fiscal_year(self):
        """
        Creates a fiscal year and requried sequences
        """
        FiscalYear = Pool().get('account.fiscalyear')
        Sequence = Pool().get('ir.sequence')

        date = datetime.date.today()

        post_move_sequence, = Sequence.create([{
            'name': '%s' % date.year,
            'code': 'account.move',
            'company': self.id,
        }])

        fiscal_year, = FiscalYear.create([{
            'name': '%s' % date.year,
            'start_date': date + relativedelta(month=1, day=1),
            'end_date': date + relativedelta(month=12, day=31),
            'company': self.id,
            'post_move_sequence': post_move_sequence.id,
        }])
        FiscalYear.create_period([fiscal_year])

    def _create_coa_minimal(self):
        """Create a minimal chart of accounts
        """
        AccountTemplate = Pool().get('account.account.template')
        Account = Pool().get('account.account')

        account_create_chart = Pool().get(
            'account.create_chart', type="wizard"
        )

        account_template, = AccountTemplate.search(
            [('parent', '=', None)]
        )

        session_id, _, _ = account_create_chart.create()
        create_chart = account_create_chart(session_id)
        create_chart.account.account_template = account_template
        create_chart.account.company = self
        create_chart.transition_create_account()

        receivable, = Account.search([
            ('kind', '=', 'receivable'),
            ('company', '=', self.id),
        ])
        payable, = Account.search([
            ('kind', '=', 'payable'),
            ('company', '=', self.id),
        ])
        create_chart.properties.company = self
        create_chart.properties.account_receivable = receivable
        create_chart.properties.account_payable = payable
        create_chart.transition_create_properties()

    @classmethod
    def signup(cls, items):
        """Creates a new company and associated user.

        items is a dictionary with follwing keys:
            shop: name of the shop
            email: unique email id
            password: password
        """
        Party = Pool().get('party.party')
        Currency = Pool().get('currency.currency')
        Company = Pool().get('company.company')
        User = Pool().get('res.user')
        ModelData = Pool().get('ir.model.data')

        if not validate_email(items.get('email')):
            cls.raise_user_error("invalid_email_address")

        with Transaction().set_context(company=None):
            company_party, = Party.create([{
                'name': items.get('shop')
            }])
            customer, = Party.create([{
                "name": "Customer [%s]" % items.get('email')
            }])
            supplier, = Party.create([{
                "name": "Supplier [%s]" % items.get('email')
            }])

            company, = Company.create([{
                'party': company_party.id,
                'currency': Currency.search([('code', '=', 'INR')])[0].id,
                'customer': customer.id,
                'supplier': supplier.id,
            }])

            group_account_admin = ModelData.get_id(
                'account', 'group_account_admin'
            )
            group_stock_admin = ModelData.get_id(
                'stock', 'group_stock_admin'
            )
            group_stock_force_assignment = ModelData.get_id(
                'stock', 'group_stock_force_assignment'
            )
            group_stock = ModelData.get_id('stock', 'group_stock')
            user, = User.create([{
                'name': items.get('shop'),
                'login': items.get('email'),
                'password': items.get('password'),
                'main_company': company.id,
                'company': company.id,
                'groups': [('add', [
                    group_account_admin,
                    group_stock_admin,
                    group_stock_force_assignment,
                    group_stock,
                ])]
            }])

        with Transaction().set_user(0):
            company._create_coa_minimal()
            company._create_fiscal_year()
