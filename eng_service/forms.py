from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from eng_service.models import EngFixer


class EngFixerForm(forms.ModelForm):
    class Meta:
        model = EngFixer
        fields = ('input_sentence', 'fixed_sentence')
        # exclude = ('id',)

        widgets = {
            'input_sentence': forms.Textarea(attrs={'rows': 2}),
            'fixed_sentence': forms.Textarea(attrs={'rows': 2}),
        }

        error_messages = {
            'input_sentence': {
                'max_length': _("This text is too long."),
            },
        }

    input_sentence = forms.CharField(max_length=256)
    # input_sentence = forms.CharField(max_length=5, widget=forms.Textarea(attrs={'rows': 2}))
    # fixed_sentence = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    # def clean_input_sentence(self):
    #     data = self.cleaned_data['input_sentence']
    #     if data != data.lower():
    #         raise ValidationError('Please use low case')
    #     return data



