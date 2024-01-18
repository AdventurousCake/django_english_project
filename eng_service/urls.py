from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from eng_service.views import CheckENGView, CheckENGViewUpdate, EngMainView, GetRandomView
from eng_service.views_profile import EngProfileView
from eng_service.views_drf import EngViewSet, UserViewSet

app_name = 'eng_service'

router = DefaultRouter()
# router.register('photos', PhotoItemViewSet)  # VSET
router.register('vset', EngViewSet)  # VSET
router.register('uvset', UserViewSet)  # VSET

urlpatterns = [
    path('', CheckENGView.as_view(), name='eng'),
    path('list/', EngMainView.as_view(), name='eng_list'),
    path('get/<int:pk>/', CheckENGViewUpdate.as_view(), name='eng_get'),

    path('profile/<int:pk>/', EngProfileView.as_view(), name='eng_profile'),
    path('random/', GetRandomView.as_view(), name='eng_random'),
]

urlpatterns += router.urls
