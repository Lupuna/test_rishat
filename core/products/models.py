from django.db import models


class Discount(models.Model):
    name = models.CharField(max_length=255)
    percentage = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"


class Tax(models.Model):
    name = models.CharField(max_length=255)
    percentage = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"


class Order(models.Model):
    class CurrencyChoices(models.TextChoices):
        EUR = "eur", "Euro"
        USD = "usd", "US Dollar"

    title = models.CharField(max_length=255)
    currency = models.CharField(
        max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.EUR
    )
    items = models.ManyToManyField("Item", related_name="orders")
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)

    def total_price(self):
        total = sum(float(item.price) for item in self.items.all())
        if self.discount:
            total *= (1 - self.discount.percentage / 100)
        if self.tax:
            total *= (1 + self.tax.percentage / 100)
        return round(total, 2)

    def __str__(self):
        return self.title


class Item(models.Model):
    class CurrencyChoices(models.TextChoices):
        EUR = "eur", "Euro"
        USD = "usd", "US Dollar"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.CharField(max_length=255)
    currency = models.CharField(
        max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.EUR
    )

    def __str__(self):
        return self.name
