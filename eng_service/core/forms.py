from django.contrib.auth.forms import UserCreationForm
from eng_service.models_core import User


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2']
