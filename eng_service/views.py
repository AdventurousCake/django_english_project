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
from eng_service.models import EngFixer, Request
# from stripe_payments.services import create_stripe_session
import logging

from eng_service.models_core import User


# TODO LIST BY USER
class EngListUserView(TemplateView, LoginRequiredMixin):
    template_name = "Eng_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        context['data_list'] = EngFixer.objects.filter()
        return context

class EngMainView(TemplateView):
    template_name = "Eng_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_list'] = EngFixer.objects.all()
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

        # form.add_error(None, '123')
        # if 'non_field_errors' in form.errors:
        #     for error in form.errors['non_field_errors']:
        #         if isinstance(error, ValidationError): #and 'unique' in error.message:
        #             # Handle the Unique constraint error here
        #             # For example, you can add a custom error message to the form
        #             form.add_error(None, 'This record violates a unique constraint.')
        #             break
        # form.add_error(None, '123')

        return super(CheckENGView, self).form_invalid(form)


    @staticmethod
    def process_data(input_str):
        input_ = input_str
        fix = eng_fixer(input_)
        fixed_result_JSON = fix.get('corrections')

        fixed_sentence = fix.get('text')

        return dict(input=input_, fixed_sentence=fixed_sentence, fixed_result_JSON=fixed_result_JSON)


    def form_valid(self, form) -> HttpResponseRedirect:
        # 25 TODO !!! form.cleaned_data
        obj: EngFixer = form.save(commit=False)

        # obj.author = self.request.user
        # logger = logging.getLogger()
        # item = EngFixer.objects.get(input_sentence=obj.input_sentence)
        # existing
        # db_item = EngFixer.objects.filter(input_sentence=obj.input_sentence).first()
        # item = EngFixer.objects.filter(input_sentence=obj.input_sentence).exists()
        # выше ПРОВЕРКА В def post FORM VALID/NON VALID
        # NONE db_item
        # if db_item:
        #     logger.warning(f'using cache: id:{db_item.id}')
        #     return redirect('eng_service:eng_get', db_item.id)

        # todo MAIN FIXER logic
        fix = eng_fixer(obj.input_sentence)

        obj.fixed_sentence = fix.get('text')
        obj.fixed_result_JSON = fix.get('corrections')



        # todo SAVE TO MODEL?
        # # type_ = fix.get('corrections')[0].get('type')
        # types_ = fix.get('error_types')
        # if types_:
        #     types_cnt_dict = Counter(types_)
        #     types_list = list(types_cnt_dict.keys())
        #     types_most = types_cnt_dict.most_common(1)[0]
        #
        #     db_list = []
        #     for item in types_list:
        #         if item in known_types:
        #             db_list.append(item)
        #         else:
        #             # create new tag?
        #             db_list.append('unknown')
        #
        #     # file
        #     with open('!ENG_TYPES.txt', 'a', encoding='utf-8') as f:
        #         # json.dump(types_cnt_dict, f, ensure_ascii=False, indent=4)
        #         f.write(',' + ','.join(types_list))

        # rephraser
        rephrases = EngRephr().get_rephrased_sentences(input_str=obj.input_sentence)
        if rephrases:
            obj.rephrases_list = rephrases

        # translate
        tr_input = Translate().get_ru_from_eng(text=obj.input_sentence)
        tr_correct = Translate().get_ru_from_eng(text=obj.fixed_sentence)

        obj.translated_RU = f"{tr_input} ->\n{tr_correct}"
        # obj.translated_RU = Translate().get_ru_from_eng(text=obj.input_sentence)

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
            # UserProfile.objects.get(user=request.user)
            profile = request.user.userprofile


        Request.objects.create(
            user_profile=profile,
            fix=obj,
        )


    def get_object(self, *args, **kwargs):
        obj = super(CheckENGViewUpdate, self).get_object(*args, **kwargs)
        # if obj.author != self.request.user:
        #     raise PermissionDenied()  # or Http404

        # 26 todo
        self.save_request(self.request, obj)

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disable_buttons'] = True

        # json to text
        # context['description'] = pprint.pformat(self.object.fixed_result_JSON, indent=4).replace('\n', '<br>')

        # TODO
        suggestions_rows = []
        data = list(self.object.fixed_result_JSON)
        if data:
            for item in data:
                # input TODO NAMING
                text = item.get('mistakeText')
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

                # sugg_list = []
                # if item:
                #     for s in suggestions:
                #         sugg_list.append(s)
                # if sugg_list:
                #     FIXED_TEXT = sugg_list[0]['text']
                #     # sugg_list = '\n'.join(map(str, sugg_list))
                #     sugg_list = '\n'.join(f"{s['text']} ({s['category']}, {s.get('definition', '')})" for s in sugg_list)

                if suggestions:
                    FIXED_TEXT = suggestions[0]['text']

                    # sugg_list = '\n'.join(map(str, sugg_list))
                    sugg_string = '\n'.join(f"{s['text']} ({s['category']}, {s.get('definition', '')})" for s in suggestions)
                else:
                    sugg_string = ""

                suggestions_rows.append((text, FIXED_TEXT, long_description, short_description, sugg_string))

                    # fix_text = item.get('text')
                    # category = item.get('category')
                    # definition = item.get('definition')
                # suggestions_rows.append((text, fix_text, category, definition, short_description, long_description))


        context['suggestions_rows'] = suggestions_rows
        context['rephrases_list'] = '\n'.join(self.object.rephrases_list) if self.object.rephrases_list else None

        context['translate'] = self.object.translated_RU

        # rephr
        # data = get_rephrased(input_str=None)

        return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = "📨 Send message form"
    #     context['btn_caption'] = "Send"
    #     context['table_data'] = Message.objects.select_related().order_by('-created_date')[:5]
    #
    #     return context

    def form_valid(self, form):
        # obj = form.save(commit=False)
        # obj.author = self.request.user

        return super(CheckENGViewUpdate, self).form_valid(form)


####################################################################################################################

# for mix detail
# https://stackoverflow.com/questions/45659986/django-implementing-a-form-within-a-generic-detailview


