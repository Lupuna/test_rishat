from unittest import TestCase

from products.models import Item, Discount, Tax, Order


class DiscountModelTestCase(TestCase):
    def setUp(self):
        self.discount = Discount.objects.create(name="Summer Sale", percentage=10)

    def test_discount_str(self):
        self.assertEqual(str(self.discount), "Summer Sale (10%)")


class TaxModelTestCase(TestCase):
    def setUp(self):
        self.tax = Tax.objects.create(name="VAT", percentage=20)

    def test_tax_str(self):
        self.assertEqual(str(self.tax), "VAT (20%)")


class OrderModelTestCase(TestCase):
    def setUp(self):
        self.item1 = Item.objects.create(name="Test Item 1", description="Item 1 Description", price="10")
        self.item2 = Item.objects.create(name="Test Item 2", description="Item 2 Description", price="20")
        self.discount = Discount.objects.create(name="Summer Sale", percentage=10)
        self.tax = Tax.objects.create(name="VAT", percentage=20)
        self.order = Order.objects.create(title="Order 1", currency="eur", discount=self.discount, tax=self.tax)
        self.order.items.set([self.item1, self.item2])

    def test_order_str(self):
        self.assertEqual(str(self.order), "Order 1")
