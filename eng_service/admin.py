from django.contrib import admin

from eng_service.models import EngFixer, UserProfile, Request

admin.site.register([Request, UserProfile, EngFixer])
