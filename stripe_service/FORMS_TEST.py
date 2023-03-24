from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from stripe_service.models import EngFixer


class EngFixerForm(forms.ModelForm):
    class Meta:
        model = EngFixer
        fields = ('input_sentence', 'fixed_result')
        # exclude = ('id',)

        widgets = {
            'input_sentence': forms.Textarea(attrs={'rows': 2}),
            'fixed_result': forms.Textarea(attrs={'rows': 2}),
        }

        error_messages = {
            'input_sentence': {
                'max_length': _("This text is too long."),
            },
        }

    input_sentence = forms.CharField(max_length=256)
    # input_sentence = forms.CharField(max_length=5, widget=forms.Textarea(attrs={'rows': 2}))
    # fixed_result = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    # def clean_input_sentence(self):
    #     data = self.cleaned_data['input_sentence']
    #     if data != data.lower():
    #         raise ValidationError('Please use low case')
    #     return data


class TestForm1(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)
    your_name2 = forms.CharField(label='Your name2', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    text = forms.CharField(widget=forms.Textarea())
    check = forms.BooleanField()
