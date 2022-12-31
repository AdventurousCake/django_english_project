
from django.forms import ModelForm, ValidationError

from service.models import MenuItem


class MenuForm(ModelForm):
    class Meta:
        model = MenuItem
        fields = '__all__'
        # exclude = ('id', 'author')


    # clean_FIELD validation
    # def clean_text(self):
    #     data = self.cleaned_data['text']
    #     if data != data.lower():
    #         raise ValidationError('Please use low case')
    #     return data