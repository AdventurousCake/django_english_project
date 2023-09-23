from django_test1.settings import *

DEBUG = False

INSTALLED_APPS.remove('debug_toolbar')
MIDDLEWARE.insert(0, 'core.middleware.simple_ip_check')
