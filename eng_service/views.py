import time
from collections import Counter
from enum import Enum

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator

from django.views.generic import TemplateView, FormView, CreateView, UpdateView
from django_ratelimit.decorators import ratelimit
from rest_framework.response import Response
from rest_framework.views import APIView

from eng_service.ENG_FIX_logic import EngFixParser, EngRephr
from eng_service.forms import EngFixerForm
from eng_service.local_lib.google_translate import Translate
from eng_service.models import EngFixer, Request, UserProfile, Tag
# from stripe_payments.services import create_stripe_session
import logging

from eng_service.models_core import User

class Parser():
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
                long_description = item.get('longDescription')
                # gramm mistake
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
                    # TEXT from first suggestion
                    fixed_text = suggestions[0]['text']
                    sugg_string = '\n'.join(
                        f"{s['text']} ({s['category']}, {s.get('definition', '')})" for s in suggestions)

                suggestions_rows.append((input_text, fixed_text, long_description, short_description, sugg_string))
        return suggestions_rows

class EngProfileView(TemplateView, LoginRequiredMixin):
    template_name = "Eng_profile.html"

    # only for user?

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # filter by user LEN; limits?

        # todo if anon user -> 404
        # get or 404
        if self.request.user.is_authenticated:
            profile = self.request.user.userprofile
        else:
            profile = None

        # profile = get_object_or_404(UserProfile, user=self.request.user)

        # profile = self.request.user.userprofile

        # todo
        profile = User.objects.get(id=1).userprofile

        requests = (Request.objects.filter(user_profile=profile)
                    .select_related('fix')
                    # .order_by('-created_date')
                    .values(
            'fix_id',
            'fix__fixed_result_JSON',  # todo
            'fix__mistakes_most_TMP', 'fix__mistakes_list_TMP',
            # 'created_date'
        )
                    .distinct()
                    # .distinct('fix_id')
                    )

        # requests = Request.objects.filter(user_profile=profile).select_related('fix').order_by('-created_date')
        # requests = Request.objects.filter(user_profile=profile).order_by('-created_date')

        count = len(requests)  # .count()
        last_using = \
            Request.objects.filter(user_profile=profile).values_list('created_date').order_by('-created_date').first()[0]
        # last_using = last_using.strftime('%Y-%m-%d %H:%M')

        ################### test
        # FROM JSON
        # tst = EngFixer.objects.values_list('fixed_result_JSON', flat=True)
        # m = []
        # for json_item in tst:
        #     for item in json_item:
        #         if 'type' in item:
        #             m.append(item['type'])

        #######################
        # x= tst[0]['fixed_result_JSON'][0]['type']

        # requests = [{'fix__mistakes_most_TMP': 'example', 'fix__fixed_result_JSON': [{'type': 'noun'}]}]
        m = []
        for item in requests:
            # tmp = item.get('fix__mistakes_most_TMP')
            # if tmp:
            #     m.append(tmp)
            # else:

            # todo to parser; if empty fix__mistakes_most_LIST
            eng_json = item.get('fix__fixed_result_JSON')
            if eng_json:
                for sentence in eng_json:
                    if 'type' in sentence:
                        m.append(sentence['type'])

        top3_str = ''
        if m:
            types_cnt_dict = Counter(m)
            top = types_cnt_dict.most_common(3)
            top3_str = '\n'.join([f'{item[0]} - {item[1]}' for item in top])

        ##############

        # select
        selected_tag = self.request.GET.get("tag") or 'Grammar'
        # todo in none
        print(selected_tag)

        # x = (EngFixer.objects
        #      # .filter(user_profile=profile)
        #      .select_related('request', 'tags')
        #      # .filter('request__user_profile', profile)
        #      # .filter(tags__name=tag)
        #      )

        profile = None # anon
        d = (Request.objects
                    # .filter(user_profile=UserProfile.objects.get(id=1))
                    .filter(user_profile=profile)
                    .select_related('fix', 'fix__tags')
                    # .prefetch_related('fix__tags')

                    # .filter(fix__tags__name=tag)

                    # .values('fix','fix__tags')
                    # .values_list('id','fix__id', 'fix__tags', 'fix__tags__name')
        # todo
                    .values('id','fix','fix__tags', 'fix__tags__name')

                    # .values('fix__fixed_sentence', 'fix__tags', 'fix__tags__name')

                    # .filter(fix__tags__name='Grammar')
                    .filter(fix__tags__name=selected_tag)
             )

        res = '\n'.join([f"""{i.get('id')} - {i.get("fix__tags__name")}""" for i in d])

        # todo simply
        # x = Request.objects.values('id','fix__tags__name', 'fix__tags').filter(fix__tags__name='Grammar')

        # res = '\n'.join([f'{item.fix.fixed_sentence}, ({[str(i) for i in item.fix.tags.all()]})' for item in d])
        # res = '\n'.join([f'{item.fix.fixed_sentence}, ({item.fix.tags.all()})' for item in d])

        context['testdata'] = res #res

        context['count'] = count
        context['last_using'] = last_using
        context['top3_str'] = top3_str
        context['data_list'] = requests
        return context


# TODO LIST BY USER; UNUSED
class EngListUserView(TemplateView, LoginRequiredMixin):
    template_name = "Eng_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        # todo filter request
        context['data_list'] = EngFixer.objects.filter()
        return context


class EngMainView(TemplateView):
    template_name = "Eng_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        LIMIT = 20
        context['data_list'] = EngFixer.objects.all().order_by('-created_date')[:LIMIT]
        return context


class CheckENGView(CreateView):  # LoginRequiredMixin
    form_class = EngFixerForm
    template_name = "Eng_form.html"

    # success_url = reverse_lazy('stripe_service:eng1_get', kwargs={'pk': self.object.pk})

    # after fixer
    def get_success_url(self):
        return reverse('eng_service:eng_get', args=(self.object.id,))  # lazy?

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
        print('ERR FORM INVALID')
        print(form.data['input_sentence'])

        form_error = form.errors['input_sentence'].data[0]
        check_unique_input = isinstance(form_error, ValidationError) and form_error.code == 'unique'

        if check_unique_input:
            # redirect if exists (ValidationError)
            obj = EngFixer.objects.values('id').get(input_sentence=form.data['input_sentence'])
            return redirect('eng_service:eng_get', obj['id'])

        return super(CheckENGView, self).form_invalid(form)

    # TODO PARSE 1
    @staticmethod
    def get_eng_data(input_str):
        start = time.perf_counter()

        fix = EngFixParser.get_parsed_data(input_str)
        fixed_result_JSON = fix.get('corrections')
        fixed_sentence = fix.get('text')
        its_correct = fix.get('its_correct')

        # TODO 03 error_types
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

    # processing form data
    # @method_decorator(ratelimit(key='ip', rate='10/m'))
    def form_valid(self, form) -> HttpResponseRedirect:
        obj: EngFixer = form.save(commit=False)

        # not obj.input_sentence, use cleaned_data
        input_str = form.cleaned_data['input_sentence']
        data = self.get_eng_data(input_str)

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

        tags = []
        for i in data['error_types']:
            tag, created = Tag.objects.get_or_create(name=i)
            tags.append(tag)
        obj.tags.add(*tags)

        # form.save()
        form.save_m2m()

        # save and redirect
        return super(CheckENGView, self).form_valid(form)


class CheckENGViewUpdate(UpdateView):  # LoginRequiredMixin
    """display data by get pk + CONTEXT FOR UPDATEVIEW"""

    """UPDATE VIEW FOR FORMS
    eng_get/<int:pk>/
    """

    model = EngFixer
    form_class = EngFixerForm
    template_name = "Eng_form.html"

    # success_url = reverse_lazy('form_msg:send_msg')

    @staticmethod
    def save_request(request, obj):
        user = request.user
        print('USER: ', user)

        profile = None
        if isinstance(user, User):  # else AnonymousUser
            # TODO GET OR CREATE
            profile = UserProfile.objects.filter(user=user).first()
            # try:
            #     profile = UserProfile.objects.get(user=user)
            # except UserProfile.DoesNotExist:
            #     pass
            #     # profile = UserProfile.objects.create(user=user)

            # profile = UserProfile.objects.get(user=request.user)
            # profile = UserProfile.objects.get_or_create(user=request.user)
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
        print(tag)

        # json to input_text
        # context['description'] = pprint.pformat(self.object.fixed_result_JSON, indent=4).replace('\n', '<br>')

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

    def form_valid(self, form):
        # obj = form.save(commit=False)
        # obj.author = self.request.user

        return super(CheckENGViewUpdate, self).form_valid(form)

####################################################################################################################

# for mix detail
# https://stackoverflow.com/questions/45659986/django-implementing-a-form-within-a-generic-detailview
