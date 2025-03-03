from unittest import TestCase
from unittest.mock import MagicMock, patch

from django.urls import reverse
from rest_framework.test import APIRequestFactory
from products.models import Item, Discount, Tax, Order
from products.views import BuyView, BuyOrderView


class BuyViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.item = Item.objects.create(name="Test Item", price="10")

    @patch("stripe.checkout.Session.create")
    def test_buy_view_creates_stripe_session(self, mock_stripe_session_create):
        result = MagicMock()
        result.id = "test_session_id"
        mock_stripe_session_create.return_value = result

        request = self.factory.get(reverse("buy_item", args=[self.item.id]))
        view = BuyView.as_view()
        response = view(request, id=self.item.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"id": "test_session_id"})

        mock_stripe_session_create.assert_called_once_with(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": self.item.name},
                    "unit_amount": int(self.item.price) * 100,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("item", args=[self.item.id])),
            cancel_url=request.build_absolute_uri(reverse("item", args=[self.item.id])),
        )


class BuyOrderViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.item = Item.objects.create(name="Test Item", price="10")

        self.discount = Discount.objects.create(name="Summer Sale", percentage=10)
        self.tax = Tax.objects.create(name="VAT", percentage=20)

        self.order = Order.objects.create(
            title="Test Order",
            currency="eur",
            discount=self.discount,
            tax=self.tax
        )
        self.order.items.set([self.item])

    @patch("stripe.checkout.Session.create")
    def test_buy_order_view_creates_stripe_session(self, mock_stripe_session_create):
        result = MagicMock()
        result.id = "test_session_id"
        mock_stripe_session_create.return_value = result

        request = self.factory.get(
            reverse("buy_order", args=[self.order.id]))
        view = BuyOrderView.as_view()
        response = view(request, id=self.order.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"id": "test_session_id"})

        mock_stripe_session_create.assert_called_once_with(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": self.item.name},
                        "unit_amount": int(self.item.price) * 100,
                    },
                    "quantity": 1,
                },
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": f"Discount: {self.discount.name}"},
                        "unit_amount": int(-self.order.total_price() * self.discount.percentage / 100) * 100,
                    },
                    "quantity": 1,
                },
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": f"Tax: {self.tax.name}"},
                        "unit_amount": int(self.order.total_price() * self.tax.percentage / 100) * 100,
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("order", args=[self.order.id])),
            cancel_url=request.build_absolute_uri(reverse("order", args=[self.order.id])),
        )