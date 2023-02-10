from django.db import models


class Item(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=False)
    description = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f"{self.id}: {self.price}"

