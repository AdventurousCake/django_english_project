from django.urls import path, include
from rest_framework.routers import DefaultRouter

from service.views_API import PhotoItemViewSet

app_name = 'service'
from service import views, views_API

router = DefaultRouter()
router.register('photos', PhotoItemViewSet)  # VSET

urlpatterns = [
    path('', include(router.urls), name='photos'),

    path('create_menu/', views.CreateMenu.as_view(), name='create'),
    # path('names', views_API.GetNames.as_view(), name='names'),
    path('names/<str:query>', views_API.GetNames.as_view(), name='names'),
]