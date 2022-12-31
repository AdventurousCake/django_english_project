from django.urls import path, include
from rest_framework.routers import DefaultRouter

from service.views_API import PhotoItemViewSet

app_name = 'service'
from service import views

router = DefaultRouter()
router.register('photos', PhotoItemViewSet)

urlpatterns = [
    path('', include(router.urls), name='photos'),

    path('create_menu/', views.CreateMenu.as_view(), name='create'),
]