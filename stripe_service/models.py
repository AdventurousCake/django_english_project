from django.db import models
from django.db.models import Sum
from django.utils.text import gettext_lazy as _


class Curr(models.TextChoices):
    EUR = 'EUR', _('Euro')
    GBP = 'GBP', _('British Pound')
    USD = 'USD', _('US Dollar')
    RUB = 'RUB', _('Russian Ruble')


class Item(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=False)
    description = models.CharField(max_length=256, null=True, blank=True)

    currency = models.CharField(choices=Curr, null=False, blank=True, default=Curr.RUB)

    def __str__(self):
        return f"{self.id}: {self.price}"


class Order(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    items = models.ManyToManyField(to=Item)  # symmetrical?

    def get_total_cost(self):
        return self.items.aggregate(Sum('price'))

    def get_discount_total_cost(self):
        # x / 100 * (100-discount)
        pass
        # return self.get_total_cost()/100 * (self.discount.first())

    def get_disc(self):
        return self.discount()

    def __str__(self):
        return f"total {self.get_total_cost()}; disc: {self.get_disc()}"


class Discount(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    orders = models.ManyToManyField(to=Order, symmetrical=True, related_name='discount')  # symmetrical?
    value = models.IntegerField(null=False, default=5)

    class Meta:
        pass
        # unique?
