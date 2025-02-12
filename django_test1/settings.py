import logging
import os
from pathlib import Path

from environs import Env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
try:
    env.read_env(path=os.path.join(BASE_DIR, '.env.dev'))
except Exception:
    logging.error('Not found .env.dev file')
    raise

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY", None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

IS_PROD = env.bool("IS_PROD", False)

# ALLOWED_HOSTS = ['*'] # non gunicorn
ENV_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0']
if ENV_HOSTS:
    ALLOWED_HOSTS.extend(ENV_HOSTS)

DJANGO_SETTINGS_MODULE = env.str("DJANGO_SETTINGS_MODULE")

# USE CORRECT NGINX PROXY proxy_set_header Host $host; ...
# https://docs.djangoproject.com/en/4.1/ref/settings/#std:setting-CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

if IS_PROD:
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# SECURE_SSL_REDIRECT = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # 'DEFAULT_PERMISSION_CLASSES': [],

    # 'DEFAULT_RENDERER_CLASSES': [
    #     'rest_framework.renderers.JSONRenderer',
    # ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/minute',  #  UserRateThrottle
        'anon': '10/minute',  # AnonRateThrottle
    },

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 'django.contrib.staticfiles',  # required for serving swagger ui's css/js files
    'drf_yasg',

    'rest_framework',
    'django_filters',
    'debug_toolbar',
    'social_django',
    # 'django_ratelimit',

    'crispy_forms',
    'crispy_bootstrap5',

    'eng_service',
]

MIDDLEWARE = [
    # debug tools
    "debug_toolbar.middleware.DebugToolbarMiddleware",

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_test1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # 'social_django.context_processors.backends',
                # 'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_test1.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# OVERRIDES IN PROD SETTINGS
DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres_TEST1',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',  # localhost
            # 'HOST': 'db',  # localhost
            'PORT': '5432',
        }
}

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }}}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake", }}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# STATIC_ROOT = BASE_DIR / "staticfiles"

# production, use in collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# dev
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static_files'),
)

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INTERNAL_IPS = [
    "127.0.0.1",
]

# crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# github auth
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_URL_NAMESPACE = 'social'

if IS_PROD:
    SOCIAL_AUTH_GITHUB_KEY = env.str('SOCIAL_AUTH_GITHUB_KEY')
    SOCIAL_AUTH_GITHUB_SECRET = env.str('SOCIAL_AUTH_GITHUB_SECRET')
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
else:
    SOCIAL_AUTH_GITHUB_KEY_LOCAL = env.str('SOCIAL_AUTH_GITHUB_KEY_LOCAL')
    SOCIAL_AUTH_GITHUB_SECRET_LOCAL = env.str('SOCIAL_AUTH_GITHUB_SECRET_LOCAL')

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',  # also SAVE default method! dont delete
)

# Redirect to home URL after login (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = '/'

RATELIMIT_ENABLE = True
