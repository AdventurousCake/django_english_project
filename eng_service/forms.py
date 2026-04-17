from django import forms
from django.utils.translation import gettext_lazy as _

from eng_service.models import EngFixer


class EngFixerForm(forms.ModelForm):
    input_sentence = forms.CharField(max_length=256, widget=forms.Textarea(attrs={'rows': 2,
                                                                                  'autofocus': True}))

    class Meta:
        model = EngFixer
        fields = ('input_sentence', 'fixed_sentence')

        error_messages = {
            'input_sentence': {
                'max_length': _("This text is too long."),
            },
        }


    # def clean_input_sentence(self):
    #     data = self.cleaned_data['input_sentence']
    #     if data != data.lower():
    #         raise ValidationError('Please use low case')
    #     return data



