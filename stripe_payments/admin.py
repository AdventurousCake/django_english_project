from django.contrib import admin

# Register your models here.
from stripe_payments.models import Item

admin.site.register(Item)
