from django.contrib import admin

from eng_service.models import EngFixer, UserProfile, Request

admin.site.register([Request, UserProfile])

admin.site.empty_value_display = 'Empty field'


class EngFixerAdmin(admin.ModelAdmin):
    list_display = ('input_sentence', 'fixed_sentence', 'its_correct', 'is_public', 'created_date')
    list_editable = ('its_correct', 'is_public')
    search_fields = ('input_sentence', 'fixed_sentence')
    list_filter = ('its_correct', 'is_public')
    list_display_links = ('input_sentence', 'fixed_sentence')
    filter_horizontal = ('tags',)


admin.site.register(EngFixer, EngFixerAdmin)
