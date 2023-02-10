from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django_test1 import settings
from stripe_service.views import CreateCheckoutSessionAPIView, ProductLandingPageView

app_name = 'stripe_service'
from service import views, views_API

# router = DefaultRouter()
# router.register('photos', PhotoItemViewSet)  # VSET

urlpatterns = [
    # path('', include(router.urls), name='photos'),
    path('item/<int:pk>/', ProductLandingPageView.as_view(), name='index'),
    path('item/<int:pk>/buy/', CreateCheckoutSessionAPIView.as_view(), name='buy'),
]
