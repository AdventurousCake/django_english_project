import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.forms import Form
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from django.views.generic import TemplateView, FormView, CreateView, UpdateView
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from stripe_service.ENG_FIX_logic import fixer, EngRephr
from stripe_service.FORMS_TEST import StripeTestForm1, EngFixerForm
from stripe_service.models import Item, Order, Discount, EngFixer
from stripe_service.services.stripe import create_stripe_session
import logging


class EngMainView(TemplateView):
    template_name = "EngMain.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_list'] = EngFixer.objects.all()
        return context


class CheckENGView(CreateView):  # LoginRequiredMixin
    form_class = EngFixerForm
    template_name = "form_ENG.html"

    # success_url = reverse_lazy('stripe_service:eng1_get', kwargs={'pk': self.object.pk})

    # after fixer
    def get_success_url(self):
        return reverse('stripe_service:eng_get', args=(self.object.id,))  # lazy?

    # initial = {'text': 'example'}
    # success_url = reverse_lazy('form_msg:send_msg')
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = "📨 Send message form"
    #     context['btn_caption'] = "Send"
    #     context['table_data'] = Message.objects.select_related().order_by('-created_date')[:5]
    #
    #     return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['description'] = pprint.pformat(self.object.CORRECT_RESPONSE)
    #     return context

    def form_valid(self, form) -> HttpResponseRedirect:
        obj: EngFixer = form.save(commit=False)
        # obj.author = self.request.user

        # todo if in cache or db then redirect
        # return redirect('stripe_service:eng_get', obj.id)
        logger = logging.getLogger()
        # item = EngFixer.objects.get(input_sentence=obj.input_sentence)

        item = EngFixer.objects.filter(input_sentence=obj.input_sentence).first()

        if item:
            logger.warning(f'using cache: id:{item.id}')
            return redirect('stripe_service:eng_get', item.id)

        # todo MAIN FIXER logic
        fix = fixer(obj.input_sentence)
        obj.fixed_result = fix.get('text')
        obj.CORRECT_RESPONSE = fix.get('corrections')
        print(obj.fixed_result)

        # rephraser TODO
        rephrases = EngRephr().get_rephrased_sentences(input_str=obj.input_sentence)
        if rephrases:
            obj.rephrases = rephrases


        # save and redirect
        return super(CheckENGView, self).form_valid(form)

    # def form_invalid(self, form):
    #     return super(CheckENGView, self).form_invalid(form)


class CheckENGViewUpdate(UpdateView):  # LoginRequiredMixin
    """display data by get pk"""

    """UPDATE VIEW FOR FORMS"""

    model = EngFixer
    form_class = EngFixerForm
    template_name = "form_ENG.html"

    # success_url = reverse_lazy('form_msg:send_msg')

    def get_object(self, *args, **kwargs):
        obj = super(CheckENGViewUpdate, self).get_object(*args, **kwargs)
        # if obj.author != self.request.user:
        #     raise PermissionDenied()  # or Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # json to text
        # context['description'] = pprint.pformat(self.object.CORRECT_RESPONSE, indent=4).replace('\n', '<br>')

        # TODO
        suggestions_rows = []
        data = list(self.object.CORRECT_RESPONSE)
        if data:
            for item in data:
                # input
                text = item.get('mistakeText')
                long_description = item.get('longDescription')

                # грамм ошибка
                short_description = item.get('shortDescription')

                # suggestions
                suggestions = item.get('suggestions')
                """'suggestions': [
                                    {
                                        'text': 'I feel',
                                        'category': 'Verb'
                                    },
                                    {
                                        'text': "I'm feel",
                                        'category': 'Spelling'
                                    },
                                    {
                                        'text': "I'm feeling",
                                        'category': 'Verb'
                                    },
                                    {
                                        'text': 'I felt',
                                        'category': 'Verb'
                                    }
                                ],"""

                FIXED_TEXT = ""

                # sugg_list = []
                # if item:
                #     for s in suggestions:
                #         sugg_list.append(s)
                # if sugg_list:
                #     FIXED_TEXT = sugg_list[0]['text']
                #     # sugg_list = '\n'.join(map(str, sugg_list))
                #     sugg_list = '\n'.join(f"{s['text']} ({s['category']}, {s.get('definition', '')})" for s in sugg_list)

                if suggestions:
                    FIXED_TEXT = suggestions[0]['text']

                    # sugg_list = '\n'.join(map(str, sugg_list))
                    sugg_string = '\n'.join(f"{s['text']} ({s['category']}, {s.get('definition', '')})" for s in suggestions)
                else:
                    sugg_string = ""

                suggestions_rows.append((text, FIXED_TEXT, long_description, short_description, sugg_string))

                    # fix_text = item.get('text')
                    # category = item.get('category')
                    # definition = item.get('definition')
                # suggestions_rows.append((text, fix_text, category, definition, short_description, long_description))


        context['suggestions_rows'] = suggestions_rows
        context['rephrases'] = '\n'.join(self.object.rephrases) if self.object.rephrases else None

        # rephr
        # data = get_rephrased(input_str=None)

        return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = "📨 Send message form"
    #     context['btn_caption'] = "Send"
    #     context['table_data'] = Message.objects.select_related().order_by('-created_date')[:5]
    #
    #     return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        # obj.author = self.request.user

        return super(CheckENGViewUpdate, self).form_valid(form)


####################################################################################################################

# for mix detail
# https://stackoverflow.com/questions/45659986/django-implementing-a-form-within-a-generic-detailview

# STRIPE
# test form
class Form1View(FormView):
    template_name = 'form_test1.html'
    form_class = StripeTestForm1
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
        # fixme
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
        # curr = order.items.first().currency

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
