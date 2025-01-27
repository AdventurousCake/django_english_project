from django_test1.settings import *

DEBUG = True

INSTALLED_APPS.remove('debug_toolbar')
# MIDDLEWARE.insert(0, 'core.middleware.simple_ip_check')

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

# TEST_DB_URL=os.getenv('TEST_DB_URL')
# if TEST_DB_URL:
#     result = urlparse(TEST_DB_URL)
#     username = result.username
#     password = result.password
#     database = result.path[1:]
#     hostname = result.hostname
#     port = result.port or '5432'
#
# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
#         'NAME': database,
#         'USER': username,
#         'PASSWORD': password,
#         'HOST': hostname,
#         'PORT': port,
#     }
# }
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }

RATELIMIT_ENABLE = True
