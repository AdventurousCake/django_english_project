from django import forms

from stripe_service.models import EngFixer


class EngFixerModel(forms.ModelForm):
    class Meta:
        model = EngFixer
        exclude = ('id',)


class TestForm1(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)
    your_name2 = forms.CharField(label='Your name2', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    text = forms.CharField(widget=forms.Textarea())
    check = forms.BooleanField()
