from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView

from photo_service.forms import MenuForm


class CreateMenu(CreateView):
    form_class = MenuForm
    template_name = "service/create.html"
    initial = {'json': '{}'}
    success_url = '/'
    # success_url = reverse_lazy('/')

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = "📨 Send message form"
    #     context['btn_caption'] = "Send"
    #     context['table_data'] = Message.objects.select_related().order_by('-created_date')[:5]
    #
    #     return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        # obj.author = self.request.user

        return super(CreateMenu, self).form_valid(form)
