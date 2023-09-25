from django import forms


class StripeTestForm1(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)
    your_name2 = forms.CharField(label='Your name2', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    text = forms.CharField(widget=forms.Textarea())
    check = forms.BooleanField()