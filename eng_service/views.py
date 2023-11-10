from collections import Counter
from enum import Enum

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from django.views.generic import TemplateView, FormView, CreateView, UpdateView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from eng_service.ENG_FIX_logic import eng_fixer, EngRephr
from eng_service.forms import EngFixerForm
from eng_service.local_lib.google_translate import Translate
from eng_service.models import EngFixer, Request, UserProfile
# from stripe_payments.services import create_stripe_session
import logging

from eng_service.models_core import User

class EngProfileView(TemplateView, LoginRequiredMixin):
    template_name = "Eng_profile.html"
    # only for user?

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # filter by user LEN; limits?

        # todo anon user
        # get or 404
        profile = get_object_or_404(UserProfile, user=self.request.user)
        # profile = self.request.user.userprofile

        requests = (Request.objects.filter(user_profile=profile)
                    .select_related('fix')
                    .order_by('-created_date')
                    .values('fix__fixed_result_JSON', # todo
                            'fix__mistakes_most_TMP', 'fix__mistakes_list_TMP', 'created_date')
                    )

        # requests = Request.objects.filter(user_profile=profile).select_related('fix').order_by('-created_date')
        # requests = Request.objects.filter(user_profile=profile).order_by('-created_date')

        count = len(requests) # .count()
        last_using = requests[0]['created_date']  # .created_date

        # todo test
        # FROM JSON
        # tst = EngFixer.objects.values_list('fixed_result_JSON', flat=True)
        # m = []
        # for json_item in tst:
        #     for item in json_item:
        #         if 'type' in item:
        #             m.append(item['type'])


        ####################### TODO RC
        # x= tst[0]['fixed_result_JSON'][0]['type']

        # requests = [{'fix__mistakes_most_TMP': 'example', 'fix__fixed_result_JSON': [{'type': 'noun'}]}]
        m=[]
        for item in requests:
            tmp = item.get('fix__mistakes_most_TMP')
            if tmp:
                m.append(tmp)
            else:
                eng_json = item['fix__fixed_result_JSON']
                if eng_json:
                    for sentence in eng_json:
                        if 'type' in sentence:
                            m.append(sentence['type'])

        top3_str = ''
        if m:
            types_cnt_dict = Counter(m)
            # types_list_unique = list(types_cnt_dict.keys())
            # types_most_tuple = types_cnt_dict.most_common(1)[0]
            # types_most = types_most_tuple[0]
            # types_most_cnt = types_most_tuple[1]

            top = types_cnt_dict.most_common(3)
            top3_str = '\n'.join([f'{item[0]} - {item[1]}' for item in top])


        context['count'] = count
        context['last_using'] = last_using
        context['top3_str'] = top3_str
        context['data_list'] = requests
        return context

# TODO LIST BY USER
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
            # obj = form.save(commit=False)  # не было запроса для взятия даты
            # get_object_or_404(EngFixer, input_sentence=form.data['input_sentence'])
            obj = EngFixer.objects.values('id').get(input_sentence=form.data['input_sentence'])
            return redirect('eng_service:eng_get', obj['id'])

        return super(CheckENGView, self).form_invalid(form)

    @staticmethod
    def get_eng_data(input_str):
        fix = eng_fixer(input_str)
        fixed_result_JSON = fix.get('corrections')

        fixed_sentence = fix.get('text')

        # TODO 03
        error_types = fix.get('error_types')
        types_most = fix.get('types_most')

        # rephraser
        rephrases_list = None
        rephrases = EngRephr().get_rephrased_sentences(input_str=input_str)
        if rephrases:
            rephrases_list = rephrases

        # translate
        translated_input = Translate().get_ru_from_eng(text=input_str)
        translated_fixed = Translate().get_ru_from_eng(text=fixed_sentence)

        return dict(input_str=input_str, fixed_sentence=fixed_sentence, fixed_result_JSON=fixed_result_JSON,
                    rephrases_list=rephrases_list, translated_input=translated_input, translated_fixed=translated_fixed,
                    types_most=types_most, error_types=error_types)


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

        tag = self.request.GET.get("tag")
        print(tag)

        # json to input_text
        # context['description'] = pprint.pformat(self.object.fixed_result_JSON, indent=4).replace('\n', '<br>')

        # TODO JSON PARSING
        suggestions_rows = []
        data = self.object.fixed_result_JSON
        if data:
            for item in list(data):
                input_text = item.get('mistakeText')
                long_description = item.get('longDescription')

                # грамм ошибка
                short_description = item.get('shortDescription')

                # suggestions
                suggestions = item.get('suggestions')

                """'suggestions': [
                                    {
                                        'text': 'I feel',
                                        'category': 'Verb'
                                    },
                                    {
                                        'text': "I'm feel",
                                        'category': 'Spelling'
                                    },
                                    {
                                        'text': "I'm feeling",
                                        'category': 'Verb'
                                    },
                                    {
                                        'text': 'I felt',
                                        'category': 'Verb'
                                    }
                                ],
                """

                FIXED_TEXT = ""

                if suggestions:
                    # first suggestion
                    FIXED_TEXT = suggestions[0]['text']

                    # sugg_list = '\n'.join(map(str, sugg_list))
                    sugg_string = '\n'.join(
                        f"{s['text']} ({s['category']}, {s.get('definition', '')})" for s in suggestions)
                else:
                    sugg_string = ""

                suggestions_rows.append((input_text, FIXED_TEXT, long_description, short_description, sugg_string))

        context['suggestions_rows'] = suggestions_rows
        # context['rephrases_list'] = '\n'.join(self.object.rephrases_list) if self.object.rephrases_list else None
        context['rephrases_list'] = self.object.rephrases_list if self.object.rephrases_list else None

        # TODO
        if self.object.mistakes_list_TMP:
            context['types_most'] = self.object.mistakes_most_TMP
            # context['error_types'] = '#'+' #'.join(self.object.mistakes_list_TMP)
            context['error_types'] = self.object.mistakes_list_TMP

        if self.object.translated_input and self.object.translated_fixed:
            # context['translate'] = f"{self.object.translated_input} ->\n{self.object.translated_fixed}"
            context['translate'] = self.object.translated_input, self.object.translated_fixed
        return context

    def form_valid(self, form):
        # obj = form.save(commit=False)
        # obj.author = self.request.user

        return super(CheckENGViewUpdate, self).form_valid(form)

####################################################################################################################

# for mix detail
# https://stackoverflow.com/questions/45659986/django-implementing-a-form-within-a-generic-detailview
