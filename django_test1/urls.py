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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.schemas import get_schema_view

from django_test1 import settings
from eng_service.core.views import core_auth, SignUp

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('eng_service.urls'), name='eng_service'),

    path('auth_github/', include('social_django.urls', namespace='social')),
    path('page_github/', core_auth, name='page_github'),
]

urlpatterns += [
    # custom login
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup', SignUp.as_view(), name='signup'),
]

urlpatterns += [
    # swagger and schema
    path('docs', TemplateView.as_view(template_name='api/swagger-ui.html',
                                         extra_context={'schema_url': 'openapi-schema'}), name='swagger-ui'),
    path('openapi', get_schema_view(
            title="My Project",
            version="1.0.0",
            permission_classes=(permissions.AllowAny,),  # IsAdminUser, IsAuthenticated
            # public=True,
        ), name='openapi-schema'),


    path('__debug__/', include('debug_toolbar.urls')),
]
# only works in debug
urlpatterns += static(settings.STATIC_URL)