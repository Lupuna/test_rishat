from django.contrib import admin

from products.models import Item, Order, Discount, Tax

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Discount)
admin.site.register(Tax)
