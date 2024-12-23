from django.urls import path
from rest_framework.routers import DefaultRouter

from eng_service.drf_api.views_drf import EngFixApiPOST, FixViewSetRO
from eng_service.views import CheckENGView, CheckENGViewUpdate, EngMainListView, GetRandomView, DeleteFixView
from eng_service.views_profile import EngProfileView

app_name = 'eng_service'

router = DefaultRouter()
router.register('api_vset', FixViewSetRO, basename='api_vset')

urlpatterns = [
    path('', CheckENGView.as_view(), name='eng'),
    path('list/', EngMainListView.as_view(), name='eng_list'),
    path('get/<int:pk>/', CheckENGViewUpdate.as_view(), name='eng_get'),
    path('delete/<int:pk>/', DeleteFixView.as_view(), name='eng_delete_fix'),

    path('profile/', EngProfileView.as_view(), name='eng_profile'),
    path('random/', GetRandomView.as_view(), name='eng_random'),

    path('api1/', EngFixApiPOST.as_view(), name='api1'),
]

urlpatterns += router.urls
