from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.urls import reverse

from django.views.generic import TemplateView
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from stripe_service.models import Item, Order, Discount
from stripe_service.services.stripe import create_stripe_session


class SuccessesView(TemplateView):
    template_name = "stripe_page/successes.html"


class CancelView(TemplateView):
    template_name = "stripe_page/cancel.html"


class OrderPageView(TemplateView):
    template_name = "stripe_page/order.html"

    # todo broken get_total_cost

    def get_context_data(self, pk, **kwargs):
        order = Order.objects.prefetch_related('items', 'discounts').get(id=pk)
        # order = Order.objects.get(id=pk)
        # order = Order.objects.select_related('items', 'discounts').get(id=pk)

        context = super(OrderPageView, self).get_context_data(**kwargs)
        context.update({
            "order": order,
            "order_id": order.id,
            "products": order.get_items(),
            "order_total": order.get_discount_total_cost()  # TODO
        })
        return context


class ProductLandingPageView(TemplateView):
    template_name = "stripe_page/index.html"

    def get_context_data(self, pk, **kwargs):
        # product = Item.objects.prefetch_related(Prefetch('order_set')).get(id=pk)
        product = Item.objects.get(id=pk)
        # product = Item.objects.prefetch_related('order_set', 'order_set__discounts').get(id=pk) # todo broken get_total_cost

        # еще больше запросов; better above
        # product = Item.objects.prefetch_related(
        #     Prefetch(
        #         'order_set',
        #         queryset=Order.objects.prefetch_related(
        #             Prefetch(
        #                 'discount_set',
        #                 queryset=Discount.objects.only('value', 'valid_until_date')
        #             )
        #         )
        #     )
        # ).get(id=pk)

        print(product)
        print(dir(product))

        # print(dir(Order))
        # print(Order.objects.get(pk=1).get_disc())
        # print(Order.objects.discount_set.all())

        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            # "STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY,
            "product": product,

            # todo!!!
            "order_total": product.price
            # "order_total": product.order_set.first().get_discount_total_cost()

            # "order_total": product.order_set.first().get_discount_total_cost()
        })
        return context


# API
# class CreateCheckoutSessionAPIView(CreateAPIView):
#     def post(self, request, *args, **kwargs):
#         pass

class CreateOrderCheckoutSessionAPIView:
    pass

# one product
class CreateCheckoutSessionAPIView(APIView):
    def get(self, request, pk):
        # product = Item.objects.get(id=pk)  # id=self.kwargs.get('pk')
        product = get_object_or_404(Item, id=pk)  # drf.get_obj
        print(product)

        # should be int
        # price = product.price

        # CENTS, tmp big price
        price = 99999
        # price = int(product.price * 100)

        session = create_stripe_session(product_name=product.id, currency=product.currency, quantity=1, price=price,
                                        redirect_url="http://127.0.0.1/stripe_service/success/",
                                        cancel_url="http://127.0.0.1/stripe_service/cancel/")
        # redirect_url=reverse("stripe_service:success"), cancel_url=reverse("stripe_service:cancel"))  # no domain link

        print(session.to_dict())
        print(session.stripe_id)
        # return redirect(session)
        return Response({'id': session.id})  # получает в index js
        # переход работает только по прямой ссылке


"""
{
  "id": "cs_test_a1W0IvBmqExHPnp2GJqLrM6fnP6JykWFIxgbxK6HJBzsExhU3fMSb6c027",
  "object": "checkout.session",
  "after_expiration": null,
  "allow_promotion_codes": null,
  "amount_subtotal": 99999,
  "amount_total": 99999,
  "automatic_tax": {
    "enabled": false,
    "status": null
  },
  "billing_address_collection": null,
  "cancel_url": "http://127.0.0.1/stripe_service/cancel/",
  "client_reference_id": null,
  "consent": null,
  "consent_collection": null,
  "created": 1678168898,
  "currency": "rub",
  "custom_fields": [
  ],
  "custom_text": {
    "shipping_address": null,
    "submit": null
  },
  "customer": null,
  "customer_creation": "if_required",
  "customer_details": null,
  "customer_email": null,
  "expires_at": 1678255298,
  "invoice": null,
  "invoice_creation": {
    "enabled": false,
    "invoice_data": {
      "account_tax_ids": null,
      "custom_fields": null,
      "description": null,
      "footer": null,
      "metadata": {
      },
      "rendering_options": null
    }
  },
  "livemode": false,
  "locale": null,
  "metadata": {
  },
  "mode": "payment",
  "payment_intent": null,
  "payment_link": null,
  "payment_method_collection": "always",
  "payment_method_options": {
  },
  "payment_method_types": [
    "card"
  ],
  "payment_status": "unpaid",
  "phone_number_collection": {
    "enabled": false
  },
  "recovered_from": null,
  "setup_intent": null,
  "shipping_address_collection": null,
  "shipping_cost": null,
  "shipping_details": null,
  "shipping_options": [
  ],
  "status": "open",
  "submit_type": null,
  "subscription": null,
  "success_url": "http://127.0.0.1/stripe_service/success/",
  "total_details": {
    "amount_discount": 0,
    "amount_shipping": 0,
    "amount_tax": 0
  },
  "url": "https://checkout.stripe.com/c/pay/cs_test_a1W0IvBmqExHPnp2GJqLrM6fnP6JykWFIxgbxK6HJBzsExhU3fMSb6c027#fidkdWxOYHwnPyd1blpxYHZxWjA0SGxsZ0lMSXddanBWX0h%2FMTxScn1UMD11blB3UXNoS2Fhd3RxbDZ3NUtwTUJ8a2l1PTNzaENzMDNiVDRWX3VJN1xwd0Fif1RvbjVJcHMxdnVrVEBsZm1fNTV3ZlA1bUpHSycpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"
}
"""
