import logging

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DetailView, ListView, DeleteView
from django_ratelimit.decorators import ratelimit

from eng_service.forms import EngFixerForm
from eng_service.models import EngFixer, Request, UserProfile, Tag
from eng_service.models_core import User
from eng_service.utils_ import ResultProcessor, SuggestionsParser


class GetRandomView(View):
    """random fixed"""
    def get(self, request):
        eng = EngFixer.objects.filter(its_correct=False).order_by('?').first()
        if not eng:
            return redirect('eng_service:eng')
        return redirect('eng_service:eng_get', pk=eng.id)

# @method_decorator(ratelimit(key='user_or_ip', rate='7/m', method='GET', block=True), name='dispatch')
# @method_decorator(cache_page(60 * 3), name="dispatch") # dispatch
class EngMainListView(ListView):
    template_name = "Eng_list.html"
    paginate_by = 10
    context_object_name = "data_list"

    queryset = EngFixer.objects.all().order_by('-created_date')

    # def dispatch(self, request, *args, **kwargs): pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@method_decorator(ratelimit(key='ip', rate='7/m', method='POST', block=True), name='post')
class CheckENGView(CreateView):  # LoginRequiredMixin
    form_class = EngFixerForm
    template_name = "Eng_form.html"

    # after fixer
    def get_success_url(self):
        return reverse_lazy('eng_service:eng_get', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # hide field from create form
        context['form'].fields['fixed_sentence'].widget = forms.HiddenInput()
        return context

    """AFTER POST METHOD VALIDATION
    def post(self, request, *args, **kwargs):
        form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
    """

    def form_invalid(self, form):
        logging.error(f"ERR FORM INVALID; input: {form.data['input_sentence']}")

        form_error = form.errors['input_sentence'].data[0]
        check_unique_input = isinstance(form_error, ValidationError) and form_error.code == 'unique'

        if check_unique_input:
            # redirect if exists (ValidationError)
            obj = EngFixer.objects.values('id').get(input_sentence=form.data['input_sentence'])
            return redirect('eng_service:eng_get', obj['id'])

        return super(CheckENGView, self).form_invalid(form)

    def form_valid(self, form) -> HttpResponseRedirect:
        obj: EngFixer = form.save(commit=False)

        # not obj.input_sentence, use cleaned_data
        input_str = form.cleaned_data['input_sentence']
        data = ResultProcessor.process_data(input_str)

        obj.fixed_sentence = data['fixed_sentence']
        obj.fixed_result_JSON = data['fixed_result_JSON']
        obj.rephrases_list = data['rephrases_list']
        obj.translated_input = data['translated_input']
        obj.translated_fixed = data['translated_fixed']

        # TMP
        obj.mistakes_list_TMP = data['error_types']
        obj.mistakes_most_TMP = data['types_most']

        obj.its_correct = data['its_correct']

        # save obj
        form.save()

        # get or create tags
        tags = []
        if data['error_types']:
            for i in data['error_types']:
                tag, created = Tag.objects.get_or_create(name=i)
                tags.append(tag)
            obj.tags.add(*tags)

        # form.save()
        form.save_m2m()

        # save and redirect
        return super(CheckENGView, self).form_valid(form)

@method_decorator(cache_page(60 * 3), name="dispatch")
class CheckENGViewUpdate(DetailView): #UpdateView):  # LoginRequiredMixin
    """
    eng_get/<int:pk>/
    """

    model = EngFixer
    template_name = "Eng_form.html"

    @staticmethod
    def save_request(request, obj):
        user = request.user
        logging.warning(f'User request: {user}')

        # save profile
        profile = None
        if isinstance(user, User):  # else AnonymousUser
            profile, created = UserProfile.objects.get_or_create(user=user)
            # profile = UserProfile.objects.filter(user=user).first()
            # profile = request.user.userprofile

        Request.objects.create(
            user_profile=profile,
            fix=obj,
        )

    def get_object(self, *args, **kwargs):
        obj = super(CheckENGViewUpdate, self).get_object(*args, **kwargs)
        # if obj.author != self.request.user:
        #     raise PermissionDenied()  # or Http404
        self.save_request(self.request, obj)

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disable_buttons'] = True

        # select
        tag = self.request.GET.get("tag")
        # json to input_text
        # context['description'] = pprint.pformat(self.object.fixed_result_JSON, indent=4).replace('\n', '<br>')

        context['fixed'] = self.object.fixed_sentence
        context['input'] = self.object.input_sentence

        context['suggestions_rows'] = SuggestionsParser.parse_json(self.object.fixed_result_JSON)
        context['rephrases_list'] = self.object.rephrases_list if self.object.rephrases_list else None

        tags = self.object.tags.values_list('name', flat=True)
        context['error_types'] = tags
        context['its_correct'] = self.object.its_correct

        # if self.object.mistakes_list_TMP:
        #     context['types_most'] = self.object.mistakes_most_TMP
            # context['error_types'] = self.object.mistakes_list_TMP

        if self.object.translated_input and self.object.translated_fixed:
            context['translate'] = self.object.translated_input, self.object.translated_fixed
        return context


class DeleteFixView(LoginRequiredMixin, DeleteView):
    model = EngFixer
    success_url = reverse_lazy('eng_service:eng_list')

    # ignore confirm template
    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(DeleteFixView, self).get_object(*args, **kwargs)
        if not self.request.user.is_superuser:
            raise PermissionDenied()  # or Http404
        return obj