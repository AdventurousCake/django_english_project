from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django_test1 import settings
from photo_service.views_API import PhotoItemViewSet

app_name = 'photo_service'
from photo_service import views, views_API

router = DefaultRouter()
router.register('photos', PhotoItemViewSet)  # VSET

urlpatterns = [
    path('', include(router.urls), name='photos'),

    path('create_menu/', views.CreateMenu.as_view(), name='create'),
    # path('names', views_API.GetOnlyNames.as_view(), name='names'),
    path('names/<str:query>', views_API.GetOnlyNames.as_view(), name='names'),
    path('search_by_names/<str:query>', views_API.GetFilteredByName.as_view(), name='search_by_names'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
