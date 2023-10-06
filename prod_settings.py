from django_test1.settings import *

DEBUG = False

INSTALLED_APPS.remove('debug_toolbar')
# MIDDLEWARE.insert(0, 'core.middleware.simple_ip_check')

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'db'),  # localhost
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
