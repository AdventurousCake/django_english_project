from django.urls import path
from rest_framework.routers import DefaultRouter

from eng_service.views import CheckENGView, CheckENGViewUpdate, EngMainListView, GetRandomView, DeleteFixView
from eng_service.views_drf import EngViewSet, UserViewSet, SearchFix, SearchStrFix, SearchList, TagViewSet
from eng_service.views_profile import EngProfileView

app_name = 'eng_service'

router = DefaultRouter()

# router.register('photos', PhotoItemViewSet)  # VSET
router.register('vset', EngViewSet)  # VSET
router.register('uvset', UserViewSet)  # VSET
router.register('tag', TagViewSet)

urlpatterns = [
    path('', CheckENGView.as_view(), name='eng'),
    path('list/', EngMainListView.as_view(), name='eng_list'),
    path('get/<int:pk>/', CheckENGViewUpdate.as_view(), name='eng_get'),
    path('delete/<int:pk>/', DeleteFixView.as_view(), name='eng_delete_fix'),

    # path('profile/<int:pk>/', EngProfileView.as_view(), name='eng_profile'),
    path('profile/', EngProfileView.as_view(), name='eng_profile'),
    path('random/', GetRandomView.as_view(), name='eng_random'),

    path('search/', SearchFix.as_view(), name='api_search'),
    path('searchstr/', SearchStrFix.as_view(), name='api_search2'),
    path('searchlist/', SearchList.as_view(), name='api_search_list'),
]

urlpatterns += router.urls
