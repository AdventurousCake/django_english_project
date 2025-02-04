from django_test1.settings import *

DEBUG = True

INSTALLED_APPS.remove('debug_toolbar')

DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
            'PORT': '5432',
        }
}

RATELIMIT_ENABLE = True
