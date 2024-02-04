import logging
import time

from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page

from django.views.generic import TemplateView, CreateView, UpdateView, DetailView, ListView
from django_ratelimit.decorators import ratelimit

from eng_service.ENG_FIX_logic import EngFixParser, EngRephr
from eng_service.forms import EngFixerForm
from eng_service.local_lib.google_translate import Translate
from eng_service.models import EngFixer, Request, UserProfile, Tag
# from stripe_payments.services import create_stripe_session

from eng_service.models_core import User

class ResultProcessor:
    @staticmethod
    def process_data(input_str):
        start = time.perf_counter()

        # fix = EngFixParser.get_parsed_data(input_str)
        fix = EngFixParser().get_parsed_data(input_str)
        fixed_result_JSON = fix.get('corrections')
        fixed_sentence = fix.get('text')
        its_correct = fix.get('its_correct')

        # TODO TMP error_types
        error_types = fix.get('error_types')
        types_most = fix.get('types_most')

        # rephraser
        rephrases_list = None
        rephrases = EngRephr().get_rephrased_sentences(input_str=input_str)
        if rephrases:
            rephrases_list = rephrases

        # translate
        TRANSLATE_ENABLED = False
        if TRANSLATE_ENABLED:
            translated_input = Translate().get_ru_from_eng(text=input_str)
            translated_fixed = Translate().get_ru_from_eng(text=fixed_sentence)
        else:
            translated_input, translated_fixed = None, None

        timing = time.perf_counter() - start

        return dict(input_str=input_str, fixed_sentence=fixed_sentence, fixed_result_JSON=fixed_result_JSON,
                    rephrases_list=rephrases_list, translated_input=translated_input, translated_fixed=translated_fixed,
                    types_most=types_most, error_types=error_types, its_correct=its_correct)

class Parser:
    @staticmethod
    def parse_json(json_data: list[dict]):
        """'fixed_result_JSON': [{'longDescription': 'Слово было написано неправильно',
                                'mistakeText': 'didnt',
                                'shortDescription': 'Орфографическая ошибка',
                                'suggestions': [{'category': 'Spelling',
                                                 'definition': 'did not',
                                                 'text': "didn't"}],
                                'type': 'Spelling'},
                               {'longDescription': 'Число глагола и подлежащего не '
                                                   'согласованы',
                                'mistakeText': 'feels',
                                'shortDescription': 'Грамматическая ошибка',
                                'suggestions': [{'category': 'Verb', 'text': 'feel'},
                                                {'category': 'Verb',
                                                 'text': 'am feeling'},
                                                {'category': 'Verb',
                                                 'text': 'have felt'}],
                                'type': 'Grammar'}],"""

        suggestions_rows = []
        if json_data:
            for item in list(json_data):
                input_text = item.get('mistakeText')
                long_description = item.get('longDescription')  # gramm mistake
                short_description = item.get('shortDescription')
                suggestions: list[dict] = item.get('suggestions')
                """'suggestions': [{
                                        'text': 'I feel',
                                        'category': 'Verb'
                                    },
                                    {
                                        'text': "I'm feel",
                                        'category': 'Spelling'
                                    },],"""

                fixed_text = ""
                sugg_string = ""
                if suggestions:
                    fixed_text = suggestions[0]['text']  # TEXT from first suggestion
                    sugg_string = '\n'.join(
                        f"{s['text']} ({s['category']}, {s.get('definition', '')})" for s in suggestions)

                suggestions_rows.append((input_text, fixed_text, long_description, short_description, sugg_string))
        return suggestions_rows

class GetRandomView(View):
    """random fixed"""
    def get(self, request):
        eng = EngFixer.objects.filter(its_correct=False).order_by('?').first()
        if not eng:
            return redirect('eng_service:eng')
        return redirect('eng_service:eng_get', pk=eng.id)

@method_decorator(ratelimit(key='user_or_ip', rate='7/m', method='GET', block=True), name='dispatch')
@method_decorator(cache_page(60 * 3), name="dispatch") # dispatch
class EngMainListView(ListView):
    template_name = "Eng_list.html"
    paginate_by = 10
    context_object_name = "data_list"

    queryset = EngFixer.objects.all().order_by('-created_date')

    # def dispatch(self, request, *args, **kwargs):
    #     pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@method_decorator(ratelimit(key='ip', rate='1/m', method='POST', block=True), name='post')
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

    # processing form data
    # from django.utils.decorators import method_decorator
    # from django_ratelimit.decorators import ratelimit
    # @method_decorator(ratelimit(key='ip', rate='10/m'))
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

        obj.mistakes_list_TMP = data['error_types']
        obj.mistakes_most_TMP = data['types_most']

        obj.its_correct = data['its_correct']

        # save obj
        form.save()

        # for db m2m
        # db_list = []
        # for item in types_list_unique:
        #     if item in known_types:
        #         db_list.append(item)
        #     else:
        #         # create new tag?
        #         db_list.append('unknown')

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

        context['suggestions_rows'] = Parser.parse_json(self.object.fixed_result_JSON)
        context['rephrases_list'] = self.object.rephrases_list if self.object.rephrases_list else None

        # TODO TAGS
        tags = self.object.tags.values_list('name', flat=True)
        context['error_types'] = tags
        context['its_correct'] = self.object.its_correct

        # if self.object.mistakes_list_TMP:
        #     context['types_most'] = self.object.mistakes_most_TMP
            # context['error_types'] = self.object.mistakes_list_TMP

        if self.object.translated_input and self.object.translated_fixed:
            context['translate'] = self.object.translated_input, self.object.translated_fixed
        return context