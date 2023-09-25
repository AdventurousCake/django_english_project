from django.db import models
from django.db.models import Sum
from django.utils.text import gettext_lazy as _

# Create your models here.

class Curr(models.TextChoices):
    EUR = 'EUR', _('Euro')
    GBP = 'GBP', _('British Pound')
    USD = 'USD', _('US Dollar')
    RUB = 'RUB', _('Russian Ruble')


class Item(models.Model):
    class Curr(models.TextChoices):
        EUR = 'EUR', 'Euro'
        GBP = 'GBP', 'British Pound'
        USD = 'USD', 'US Dollar'
        RUB = 'RUB', 'Russian Ruble'

    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=False)
    description = models.CharField(max_length=256, null=True, blank=True)

    currency = models.CharField(choices=Curr.choices, null=False, blank=True, default=Curr.RUB, max_length=50)

    def __str__(self):
        return f"{self.id}: {self.price}"


class Order(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    items = models.ManyToManyField(to=Item)  # symmetrical?
    discounts = models.ManyToManyField('Discount', related_name='orders')

    def get_items(self):
        return self.items.all()

    def _set_discount(self):
        pass

    def get_curr(self):
        return 'USD'  # Todo

    def get_total_cost(self):
        # todo 3 ДУБЛЯ
        # return 99

        return self.items.aggregate(Sum('price')).get('price__sum')  # broken to many req
        # return sum(item.price for item in self.get_items())  # +w

    def get_discount_total_cost(self):
        # x / 100 * (100-discount)
        return self.get_total_cost() / 100 * (100 - self.get_disc())

    def get_disc(self):
        # return self.discount_set.all()
        if self.discounts.exists():  # self.discount_set
            # if self.discounts.first().exists():
            return self.discounts.first().value
        else:
            return 0

    def __str__(self):
        return f"total {self.get_total_cost()}; total-disc: {self.get_discount_total_cost()} ; disc: {self.get_disc()}"


# todo
# - dicount - orders table
# migration with data?

# from stripe_service.models import Order2, Item
#  Order2.objects.get(pk=1).discount2_set.first().value
# todo https://metanit.com/python/django/5.7.php

# множество заказов и множество скидок
class Discount(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    # orders = models.ManyToManyField(to=Order, related_name='discount_set')  # related_name='discount')  # symmetrical?
    value = models.IntegerField(null=False, default=5)
    valid_until_date = models.DateTimeField()

    class Meta:
        pass
        # unique?


# in m2m rel models; delete by remove() or clear, not db logic
class OrderDiscountTest(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    order_id = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    discount_id = models.ForeignKey(to=Discount, on_delete=models.CASCADE)

# # TEST
# class Order2(models.Model):
#     items = models.ManyToManyField(Item)
#
#     def __str__(self):
#         return f"total: {self.total_cost}; disc: {self.disc}"
#
#     @property
#     def total_cost(self):
#         return self.items.aggregate(Sum('price'))['price__sum']
#
#     @property
#     def disc(self):
#         return self.discount2_set.all()
#
#     # @property
#     # def discount_total_cost(self):
#     #     pass
#     #     # return self.total_cost / 100 * (100 - self.discount.value)
#
#
# class Discount2(models.Model):
#     orders = models.ManyToManyField(Order2, related_name='discount2_set')
#     value = models.PositiveIntegerField(default=5)
#     valid_until_date = models.DateTimeField()
