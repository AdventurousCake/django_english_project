"""django_test1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('photo_service.urls'), name='photo_service'),

    path('stripe_payments/', include('stripe_payments.urls'), name='stripe_payments'),
    path('eng/', include('eng_service.urls'), name='eng_service'),

    path('b/', include('BOOKS.urls'), name='books_service'),
]


urlpatterns += [
    path('__debug__/', include('debug_toolbar.urls')),
]