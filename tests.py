#! -*- coding: utf-8 -*-

from random import randrange
from unittest import TestCase
import unipag
from unipag import defaults, NotFound, Unauthorized


class LiveAPITest(TestCase):
    def setUp(self):
        # unittest user, live mode, secret
        defaults.api_key = 'sdEzLtip2wkZusq7MDNBHs3C'

    def test_get_connections(self):
        connections = unipag.Connection.list()
        self.assertTrue(isinstance(connections, list))
        self.assertTrue(len(connections) > 0)
        for conn in connections:
            self.assertTrue(isinstance(conn, unipag.Connection))

    def test_invoices(self):
        invoice = unipag.Invoice(amount=1, currency='USD').save()
        invoice2 = unipag.Invoice.get(id=invoice.id)
        self.assertTrue(isinstance(invoice2, unipag.Invoice))
        self.assertEqual(invoice, invoice2)
        invoice2.delete()
        self.assertFalse(invoice.deleted)
        invoice.reload()
        self.assertTrue(invoice.deleted)

    def test_payments(self):
        # Generate 3 random payments for some invoice
        invoice = unipag.Invoice(amount=10, currency='RUB').save()
        for i in range(3):
            unipag.Payment.create(
                amount=randrange(1, invoice.amount),
                invoice=invoice.id,
                payment_gateway='masterbank.ru'
            )
        # Generate 3 stand-alone payments
        for i in range(3):
            unipag.Payment.create(
                amount=randrange(1, invoice.amount),
                currency='RUB',
                payment_gateway='masterbank.ru'
            )
        # Check that only payments linked to invoice are returned
        payments = unipag.Payment.list(invoice=invoice.id)
        self.assertTrue(isinstance(payments, list))
        self.assertEqual(len(payments), 3)
        for p in payments:
            self.assertTrue(isinstance(p, unipag.Payment))
            self.assertEqual(p.invoice, invoice.id)

    def test_invoice_custom_data(self):
        test_dict = {
            u'int': 1,
            u'float': 3.14159,
            u'str': u'Hi there',
            u'None': None,
            u'true': True,
            u'false': False,
            u'int_str': u'2',
            u'float_str': u'2.71828',
            u'None_str': u'None',
            u'true_str': u'true',
            u'false_str': u'false',
            u'array': [1, 1.5, u'a', None, True],
            u'obj': {
                u'int_key': 42,
                u'float_key': 90.0,
                u'str_key': u'®',
                u'array': [1, 2, False],
                u'obj': {u'None': None}
            }
        }
        inv1 = unipag.Invoice.create(
            amount=3.2,
            currency='RUB',
            description=u'®',
            custom_data=test_dict,
        )
        self.assertEqual(test_dict, inv1.custom_data)
        inv2 = unipag.Invoice.get(id=inv1.id)
        self.assertEqual(inv2.amount, 3.2)
        self.assertEqual(inv2.currency, 'RUB')
        self.assertEqual(inv2.description, u'®')
        self.assertEqual(test_dict, inv2.custom_data)

    def test_delete_non_existing_invoice(self):
        try:
            unipag.Invoice.delete_id("111242424242")
        except NotFound as e:
            self.assertEqual(404, e.http_code)
            self.assertTrue('error' in e.json_body)
        except Exception as e:
            self.fail(
                "NotFound exception expected, but actual was %s" % type(e)
            )
        else:
            self.fail('No exception was thrown')

    def test_delete_with_wrong_api_key(self):
        try:
            unipag.Invoice.delete_id("111242424242", api_key="wrong-key")
        except Unauthorized as e:
            self.assertEqual(401, e.http_code)
            self.assertTrue('error' in e.json_body)
        except Exception as e:
            self.fail(
                "Unauthorized exception expected, but actual was %s" % type(e)
            )
        else:
            self.fail('No exception was thrown')
