from django.db.models import Prefetch
from django.shortcuts import render
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

    def get_context_data(self, pk, **kwargs):
        order = Order.objects.get(id=pk)
        # order = Order.objects.select_related('items').get(id=pk)

        context = super(OrderPageView, self).get_context_data(**kwargs)
        context.update({
            "order": order,
            "products": order.items.all(),
            "order_total": order.get_discount_total_cost()
        })
        return context


class ProductLandingPageView(TemplateView):
    template_name = "stripe_page/index.html"

    def get_context_data(self, pk, **kwargs):
        # fixme
        # product = Item.objects.prefetch_related(Prefetch('order_set')).get(id=pk)
        product = Item.objects.get(id=pk)

        # еще больше запросов
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

        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            # "STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY,
            "product": product,
            "order_total": product.order_set.first().get_discount_total_cost()
            # "order_total": product.order_set.first().get_discount_total_cost()
        })
        return context


# API
class CreateCheckoutSessionAPIView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        pass


# one product
class CreateCheckoutSessionAPIView(APIView):
    def get(self, request, pk):
        # product = Item.objects.get(id=pk)  # id=self.kwargs.get('pk')
        product = get_object_or_404(Item, id=pk)  # drf.get_obj
        print(product)

        # todo stripe logic
        # create_stripe_session(product_name=product.id, currency=product.currency, quantity=1,
        # redirect_url=reverse("stripe_service:success"), cancel_url=reverse("stripe_service:cancel"))
        create_stripe_session(product_name=product.id, price=product.price, currency=product.currency, quantity=1,
                              redirect_url=reverse("stripe_service:success"),
                              cancel_url=reverse("stripe_service:cancel"))

        return Response({})


# many
class CreateOrderCheckoutSessionAPIView(APIView):
    def get(self, request, pk):
        # product = Item.objects.get(id=pk)  # id=self.kwargs.get('pk')
        order = get_object_or_404(Order, id=pk)  # drf.get_obj
        print(order)

        curr = order.items.first().currency
        price = order.get_total_cost()

        # todo stripe logic
        create_stripe_session(product_name=order.id, price=price, currency=curr, quantity=1,
                              redirect_url=reverse("stripe_service:success"),
                              cancel_url=reverse("stripe_service:cancel"))

        return Response({})
