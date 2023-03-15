from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django_test1 import settings
from stripe_service.views import CreateCheckoutSessionAPIView, ProductLandingPageView, OrderPageView, SuccessesView, \
    CancelView, CreateOrderCheckoutSessionAPIView, Form1View

app_name = 'stripe_service'
from service import views, views_API

# router = DefaultRouter()
# router.register('photos', PhotoItemViewSet)  # VSET

urlpatterns = [
    # path('', include(router.urls), name='photos'),
    path('item/<int:pk>/', ProductLandingPageView.as_view(), name='index'),
    path('item/<int:pk>/buy/', CreateCheckoutSessionAPIView.as_view(), name='buy'),

    path('order/<int:pk>/buy/', CreateOrderCheckoutSessionAPIView.as_view(), name='order_buy'),
    path('order/<int:pk>/', OrderPageView.as_view(), name='order'),

    path('success/', SuccessesView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel'),

    # test
    path('form1/', Form1View.as_view(), name='form_test1'),
]
