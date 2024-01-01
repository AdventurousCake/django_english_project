from django.urls import path, include
from rest_framework.routers import DefaultRouter

from BOOKS_drf.views import CreateMix

app_name = 'BOOKS'
router = DefaultRouter()
router.register('create_router', CreateMix, basename='create')

urlpatterns = [
    # path('create/', CreateMix.as_view(), name='create'),
    path('', include(router.urls)),
]
