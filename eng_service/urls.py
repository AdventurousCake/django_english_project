from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from eng_service.views import CheckENGView, CheckENGViewUpdate, EngMainView, EngProfileView

app_name = 'eng_service'

# router = DefaultRouter()
# router.register('photos', PhotoItemViewSet)  # VSET

urlpatterns = [
    path('', CheckENGView.as_view(), name='eng'),
    path('eng_list/', EngMainView.as_view(), name='eng_list'),
    path('eng_get/<int:pk>/', CheckENGViewUpdate.as_view(), name='eng_get'),

    path('eng_profile/<int:pk>/', EngProfileView.as_view(), name='eng_profile'),
]
