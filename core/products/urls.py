from django.urls import path
from products.views import BuyView, ItemView, BuyOrderView

urlpatterns = [
    path('buy/item/<int:id>', BuyView.as_view(), name='buy_item'),
    path('item/<int:pk>', ItemView.as_view(), name='item'),
    path('order/<int:pk>', ItemView.as_view(), name='order'),
    path("buy/order/<int:id>/", BuyOrderView.as_view(), name="buy_order"),
]
