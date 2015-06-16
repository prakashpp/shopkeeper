# -*- coding: utf-8 -*-
"""
    shipment.py

    :copyright: (c) 2014 by Shopkeeper team, see AUTHORS.
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta
from trytond.rpc import RPC
from trytond.transaction import Transaction
from trytond.pool import Pool

__metaclass__ = PoolMeta
__all__ = ['ShipmentIn']


class ShipmentIn:
    __name__ = 'stock.shipment.in'

    @classmethod
    def __setup__(cls):
        super(ShipmentIn, cls).__setup__()
        cls.__rpc__.update({
            'mark_bought': RPC(readonly=False),
        })

    @classmethod
    def mark_bought(cls, items):
        """This method takes list of dictionary as follows:
            {
                "product": product_id,
                "quantity": quantity,
                "unit_price": unit_price,
            }

        Creates supplier shipment and account moves.
        """
        Company = Pool().get('company.company')
        StockMove = Pool().get('stock.move')
        AccountMove = Pool().get('account.move')
        AccountMoveLine = Pool().get('account.move.line')
        Journal = Pool().get('account.journal')
        Account = Pool().get('account.account')
        Product = Pool().get('product.product')
        Location = Pool().get('stock.location')

        company = Company(Transaction().context.get('company'))
        cash_journal, = Journal.search([('name', '=', 'Cash')])
        main_revenue, = Account.search([('name', '=', 'Main Revenue')])
        main_payable, = Account.search([('name', '=', 'Main Payable')])
        supplier_location, = Location.search([('name', '=', 'Supplier')])
        input_location, = Location.search([('name', '=', 'Input Zone')])

        shipment = cls(supplier=company.supplier)
        shipment.on_change_supplier()

        incoming_moves = []
        account_moves = []
        for item in items:
            product = Product(item.get('product'))
            stock_move = StockMove(
                product=product,
                uom=product.default_uom,
                quantity=item.get('quantity'),
                unit_price=item.get('unit_price'),
                from_location=supplier_location,
                to_location=input_location,
            )

            account_move = AccountMove(
                journal=cash_journal,
                origin=stock_move,
            )
            debit_line = AccountMoveLine(
                account=main_revenue,
                debit=item.get('quantity') * item.get('unit_price'),
            )
            credit_line = AccountMoveLine(
                account=main_payable,
                credit=item.get('quantity') * item.get('unit_price'),
                party=company.supplier,
            )
            account_move.lines = [debit_line, credit_line]

            incoming_moves.append(stock_move)
            account_moves.append(account_move)

        shipment.incoming_moves = incoming_moves
        shipment.save()

        cls.receive([shipment])
        cls.done([shipment])

        saved_account_moves = []
        for account_move in account_moves:
            account_move.save()
            saved_account_moves.append(account_move)

        AccountMove.post(account_moves)


class ShipmentOut:
    __name__ = 'stock.shipment.out'

    @classmethod
    def __setup__(cls):
        super(ShipmentOut, cls).__setup__()
        cls.__rpc__.update({
            'mark_sold': RPC(readonly=False),
        })

    @classmethod
    def mark_sold(cls, items):
        """This method takes list of dictionary as follows:
            {
                "product": product_id,
                "quantity": quantity,
                "unit_price": unit_price,
            }

        Creates customer shipment and account moves.
        """
        Company = Pool().get('company.company')
        StockMove = Pool().get('stock.move')
        AccountMove = Pool().get('account.move')
        AccountMoveLine = Pool().get('account.move.line')
        Journal = Pool().get('account.journal')
        Account = Pool().get('account.account')
        Product = Pool().get('product.product')
        Location = Pool().get('stock.location')

        company = Company(Transaction().context.get('company'))
        cash_journal, = Journal.search([('name', '=', 'Cash')])
        main_revenue, = Account.search([('name', '=', 'Main Revenue')])
        main_receivable, = Account.search([('name', '=', 'Main Receivable')])
        customer_location, = Location.search([('name', '=', 'Customer')])
        output_location, = Location.search([('name', '=', 'Output Zone')])

        shipment = cls(customer=company.customer)
        shipment.on_change_customer()

        outgoing_moves = []
        account_moves = []
        for item in items:
            product = Product(item.get('product'))
            stock_move = StockMove(
                product=product,
                uom=product.default_uom,
                quantity=item.get('quantity'),
                unit_price=item.get('unit_price'),
                from_location=output_location,
                to_location=customer_location,
            )

            account_move = AccountMove(
                journal=cash_journal,
                origin=stock_move,
            )
            debit_line = AccountMoveLine(
                account=main_receivable,
                debit=item.get('quantity') * item.get('unit_price'),
                party=company.customer,
            )
            credit_line = AccountMoveLine(
                account=main_revenue,
                credit=item.get('quantity') * item.get('unit_price'),
            )
            account_move.lines = [debit_line, credit_line]

            outgoing_moves.append(stock_move)
            account_moves.append(account_move)

        shipment.outgoing_moves = outgoing_moves
        shipment.save()

        cls.wait([shipment])
        cls.assign([shipment])
        cls.pack([shipment])
        cls.done([shipment])

        saved_account_moves = []
        for account_move in account_moves:
            account_move.save()
            saved_account_moves.append(account_move)

        AccountMove.post(account_moves)
