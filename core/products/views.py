import stripe as stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Item, Order


class BuyView(APIView):
    def get(self, request, id):
        item = get_object_or_404(Item, id=id)
        stripe.api_key = settings.STRIPE_SECRET_KEY_EUR if item.currency == 'eur' else settings.STRIPE_SECRET_KEY_USD
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": item.currency,
                    "product_data": {"name": item.name},
                    "unit_amount": int(item.price) * 100,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("item", args=[id])),
            cancel_url=request.build_absolute_uri(reverse("item", args=[id]))

        )
        return Response({"id": session.id})


class BuyOrderView(APIView):
    def get(self, request, id):
        order = get_object_or_404(Order, id=id)
        stripe.api_key = settings.STRIPE_SECRET_KEY_EUR if order.currency == 'eur' else settings.STRIPE_SECRET_KEY_USD

        line_items = []
        for item in order.items.all():
            line_items.append({
                "price_data": {
                    "currency": order.currency,
                    "product_data": {"name": item.name},
                    "unit_amount": int(item.price) * 100,
                },
                "quantity": 1,
            })

        if order.discount:
            line_items.append({
                "price_data": {
                    "currency": order.currency,
                    "product_data": {"name": f"Discount: {order.discount.name}"},
                    "unit_amount": int(-order.total_price() * order.discount.percentage / 100) * 100,
                },
                "quantity": 1,
            })

        if order.tax:
            line_items.append({
                "price_data": {
                    "currency": order.currency,
                    "product_data": {"name": f"Tax: {order.tax.name}"},
                    "unit_amount": int(order.total_price() * order.tax.percentage / 100) * 100,
                },
                "quantity": 1,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=request.build_absolute_uri(reverse("order", args=[id])),
            cancel_url=request.build_absolute_uri(reverse("order", args=[id]))
        )

        return Response({"id": session.id})


class ItemView(DetailView):
    model = Item
    template_name = "products/item.html"
    context_object_name = "item"
    extra_context = {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    }


class OrderView(DetailView):
    model = Order
    template_name = "products/order.html"
    context_object_name = "order"

    def get_queryset(self):
        return self.model.objects.prefetch_related('items').all()

    def get_context_data(self, **kwargs):
        order = self.get_object()
        kwargs = super().get_context_data(**kwargs)
        kwargs['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        kwargs['items'] = order.items.all()
        kwargs['discount'] = getattr(order, "discount", 0)
        kwargs['tax'] = getattr(order, "tax", 0)
        return kwargs

