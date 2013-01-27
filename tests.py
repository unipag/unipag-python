from random import randrange
from unittest import TestCase
import unipag
from unipag import defaults

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