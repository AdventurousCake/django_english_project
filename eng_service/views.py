from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from django.views.generic import TemplateView, FormView, CreateView, UpdateView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from eng_service.ENG_FIX_logic import fixer, EngRephr
from eng_service.forms import EngFixerForm
from eng_service.models import EngFixer
# from stripe_payments.services import create_stripe_session
import logging


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

    # initial = {'text': 'example'}
    # success_url = reverse_lazy('form_msg:send_msg')
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = "📨 Send message form"
    #     context['btn_caption'] = "Send"
    #     context['table_data'] = Message.objects.select_related().order_by('-created_date')[:5]
    #
    #     return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['description'] = pprint.pformat(self.object.CORRECT_RESPONSE)
    #     return context

    # def post(self, request, *args, **kwargs):
    #     pass

    """AFTER POST METHOD VALIDATION
    def post(self, request, *args, **kwargs):
        form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
    
    """

    # TODO SAVE UNIQUE, FIX LOGIC PROCESS

    def form_invalid(self, form):
        print('ERR FORM INVALID')
        return super(CheckENGView, self).form_invalid(form)

    def form_valid(self, form) -> HttpResponseRedirect:
        obj: EngFixer = form.save(commit=False)

        # TODO !!! form.cleaned_data

        # obj.author = self.request.user

        # todo if in cache or db then redirect
        # return redirect('stripe_service:eng_get', obj.id)
        logger = logging.getLogger()
        # item = EngFixer.objects.get(input_sentence=obj.input_sentence)

        # existing
        db_item = EngFixer.objects.filter(input_sentence=obj.input_sentence).first()
        # item = EngFixer.objects.filter(input_sentence=obj.input_sentence).exists()

        if db_item:
            logger.warning(f'using cache: id:{db_item.id}')
            return redirect('eng_service:eng_get', db_item.id,
                            # use_cache=True
                            )

        # todo MAIN FIXER logic
        fix = fixer(obj.input_sentence)
        obj.fixed_result = fix.get('text')
        obj.CORRECT_RESPONSE = fix.get('corrections')
        print(obj.fixed_result)

        # rephraser
        rephrases = EngRephr().get_rephrased_sentences(input_str=obj.input_sentence)
        if rephrases:
            obj.rephrases = rephrases


        # save and redirect
        return super(CheckENGView, self).form_valid(form)

    # def form_invalid(self, form):
    #     return super(CheckENGView, self).form_invalid(form)


class CheckENGViewUpdate(UpdateView):  # LoginRequiredMixin
    """display data by get pk + CONTEXT FOR UPDATEVIEW"""

    """UPDATE VIEW FOR FORMS
    eng_get/<int:pk>/
    """

    model = EngFixer
    form_class = EngFixerForm
    template_name = "Eng_form.html"

    # success_url = reverse_lazy('form_msg:send_msg')

    def get_object(self, *args, **kwargs):
        obj = super(CheckENGViewUpdate, self).get_object(*args, **kwargs)
        # if obj.author != self.request.user:
        #     raise PermissionDenied()  # or Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # json to text
        # context['description'] = pprint.pformat(self.object.CORRECT_RESPONSE, indent=4).replace('\n', '<br>')

        # TODO
        suggestions_rows = []
        data = list(self.object.CORRECT_RESPONSE)
        if data:
            for item in data:
                # input
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
                                ],"""

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
        context['rephrases'] = '\n'.join(self.object.rephrases) if self.object.rephrases else None

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


