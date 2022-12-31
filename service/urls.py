from django.urls import path

app_name = 'service'
from service import views

urlpatterns = [
    path('create/', views.CreateMenu.as_view(), name='create'),
]