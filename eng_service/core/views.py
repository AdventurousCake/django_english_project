from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from eng_service.core.forms import SignupForm
from eng_service.models import UserProfile


def core_auth(request):
    return render(request, 'github.html')


class SignUp(CreateView):
    form_class = SignupForm
    success_url = reverse_lazy("eng_service:eng")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        # login
        user = authenticate(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
        )
        if user:
            # create profile
            profile, created = UserProfile.objects.get_or_create(user=user)

            login(self.request, user)
        return response
