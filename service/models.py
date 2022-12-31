from django.db import models


class MenuItem(models.Model):
    id = models.BigAutoField(null=False, unique=True, primary_key=True,
                             auto_created=True)
    json = models.JSONField(null=False, max_length=150, blank=False)

    created_date = models.DateTimeField(null=False, auto_now_add=True)
    updated_date = models.DateTimeField(null=False, auto_now=True)


class PhotoItem(models.Model):
    id = models.BigAutoField(null=False, unique=True, primary_key=True,
                             auto_created=True)
    description = models.CharField(null=True, max_length=150)
    name = models.CharField(null=True, max_length=150)
    created_date = models.DateTimeField(null=False, auto_now_add=True)

    lat = models.DecimalField(_('Latitude'), max_digits=10, decimal_places=8)
    lng = models.DecimalField(_('Longitude'), max_digits=11, decimal_places=8)