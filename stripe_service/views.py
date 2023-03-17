from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.urls import reverse

from django.views.generic import TemplateView, FormView
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from stripe_service.FORMS_TEST import TestForm1
from stripe_service.models import Item, Order, Discount
from stripe_service.services.stripe import create_stripe_session


# test form
class Form1View(FormView):
    template_name = 'form_test1.html'
    form_class = TestForm1
    success_url = '/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # form.send_email()
        return super().form_valid(form)


class SuccessesView(TemplateView):
    template_name = "stripe_page/successes.html"


class CancelView(TemplateView):
    template_name = "stripe_page/cancel.html"


class OrderPageView(TemplateView):
    template_name = "stripe_page/order.html"

    # todo broken get_total_cost

    # Order.objects.get(id=pk).items.clear() #  clear all from the relationship; remove(item) - one

    def get_context_data(self, pk, **kwargs):
        order = get_object_or_404(Order.objects.prefetch_related('items', 'discounts'), id=pk)

        # order = Order.objects.prefetch_related('items', 'discounts').get(id=pk)

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
        product = get_object_or_404(Item, id=pk)
        # product = Item.objects.get(id=pk)
        # product = Item.objects.prefetch_related('order_set', 'order_set__discounts').get(id=pk) #  broken get_total_cost

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

# check user, price
class CreateOrderCheckoutSessionAPIView(APIView):
    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk)  # drf.get_obj
        print(order)


        # CENTS, tmp big price
        price = int(order.get_discount_total_cost() * 100)
        curr = 'RUB'

        session = create_stripe_session(product_name=order.id, currency=curr, quantity=1, price=price,
                                        redirect_url="http://127.0.0.1/stripe_service/success/",
                                        cancel_url="http://127.0.0.1/stripe_service/cancel/")
        # redirect_url=reverse("stripe_service:success"), cancel_url=reverse("stripe_service:cancel"))  # no domain link

        print(session.to_dict())
        print(session.stripe_id)
        return Response({'id': session.id})


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
