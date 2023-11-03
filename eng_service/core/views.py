from django.shortcuts import render


def core_auth(request):
    return render(request, 'github.html')