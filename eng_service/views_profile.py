from collections import Counter
from datetime import timedelta, datetime
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Value, CharField
from django.db.models.functions import Concat, Now
from django.views.generic import TemplateView

from eng_service.ENG_FIX_logic import EngFixParser
from eng_service.models import Request, EngFixer, Tag
from eng_service.models_core import User


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

        # todo; need creating profile!
        profile = User.objects.get(id=1).userprofile

        requests = (Request.objects.filter(user_profile=profile)
                    .select_related('fix')
                    # .order_by('-created_date')
                    .values(
            'fix_id',
            'fix__fixed_result_JSON',  # todo
            'fix__mistakes_most_TMP', 'fix__mistakes_list_TMP'
            # 'created_date'
        )
                    .distinct()
                    # .distinct('fix_id')
                    )

        # requests = Request.objects.filter(user_profile=profile).select_related('fix').order_by('-created_date')

        count = len(requests)  # .count()
        count_correct = Request.objects.filter(user_profile=profile).select_related('fix').filter(
            fix__its_correct=True)#.count()
        count_correct_c = count_correct.count()

        last_using = (Request.objects.filter(user_profile=profile).values_list('created_date')
        .order_by('-created_date').first()[0])
        # last_using = last_using.strftime('%Y-%mistakes-%d %H:%M')

        # todo 16
        count_lastweek = requests.filter(created_date__gte=Now() - timedelta(days=7)).count()
        count_correct_lastweek = count_correct.filter(created_date__gte=Now() - timedelta(days=7)).count()# or 0

        mistakes = []
        for item in requests:
            mistakes.extend(EngFixParser.parse_item_mistakes(item))
        top3_str = ''
        top3 = None
        if mistakes:
            types_cnt_dict = Counter(mistakes)
            top3 = types_cnt_dict.most_common(3)
            top3_str = '\n'.join([f'{item[0]} - {item[1]}' for item in top3])

        ##############

        # select test
        selected_tag = self.request.GET.get("tag") or 'Grammar'
        # todo in none
        print(selected_tag)

        # x = (EngFixer.objects
        #      # .filter(user_profile=profile)
        #      .select_related('request', 'tags')
        #      # .filter('request__user_profile', profile)
        #      # .filter(tags__name=tag)
        #      )

        profile = None  # anon
        data_tags = (Request.objects
                     # .filter(user_profile=UserProfile.objects.get(id=1))
                     .filter(user_profile=profile)
                     .select_related('fix', 'fix__tags')
                     # .prefetch_related('fix__tags')

                     # .filter(fix__tags__name=tag)

                     # .values('fix','fix__tags')
                     # .values_list('id','fix__id', 'fix__tags', 'fix__tags__name')

                     .annotate(
            tag_names=ArrayAgg('fix__tags__name',
                               # distinct=True
                               ))
                     .annotate(tag_names2=Concat('fix__tags__name', Value(', '), output_field=CharField()))

                     # todo
                     .values('id', 'fix', 'fix__tags', 'fix__tags__name', 'tag_names', 'tag_names2')

                     # .values('fix__fixed_sentence', 'fix__tags', 'fix__tags__name')

                     # .filter(fix__tags__name='Grammar')
                     .filter(fix__tags__name=selected_tag)
                     .order_by('-created_date')

        [:10]
                     )
        # pprint(str(data_tags.query))
        # res = '\n'.join([f"""{i.get('id')} - {i.get("fix__tags__name")}; {i.get('fix__tags')}; {i.get('tag_names')};
        # {i.get('tag_names2')}"""
        #                  for i in data_tags])

        data = (Request.objects
                .filter(user_profile=profile, fix__tags__name=selected_tag)
                .select_related('fix')  # 'fix__tags')
                # .values('id', 'fix__id', 'fix__input_sentence', 'fix__fixed_sentence')
                .values('fix__id', 'fix__input_sentence', 'fix__fixed_sentence')
                .distinct('fix__id')
                # .order_by('-created_date')

        [:10])
        res = '\n'.join(
            [f'fix_id: {i.get("fix__id")}\n({i.get("fix__input_sentence")} ->\n{i.get("fix__fixed_sentence")})\n' for i
             in data])

        # d2 = (EngFixer.objects.filter(
        #     tags__name=selected_tag)
        #       .select_related('tags')
        #       .annotate(tag_names=ArrayAgg('tags__name', distinct=True))
        #       .values('id', 'fixed_sentence', 'tags__name'))
        #
        # pprint(str(d2.query))

        # todo simply
        # x = Request.objects.values('id','fix__tags__name', 'fix__tags').filter(fix__tags__name='Grammar')

        # res = '\n'.join([f'{item.fix.fixed_sentence}, ({[str(i) for i in item.fix.tags.all()]})' for item in d])
        # res = '\n'.join([f'{item.fix.fixed_sentence}, ({item.fix.tags.all()})' for item in d])

        context['testdata'] = res  # res

        # TODO RANDOM; not correct
        r = EngFixer.objects.filter(its_correct=False).order_by('?').first()
        context['random_sentence'] = r.input_sentence
        context['random_sentence2'] = r.fixed_sentence
        context['random_sentence_url'] = r.get_absolute_url()

        # todo 16 2
        context['count'] = count
        context['count_correct'] = count_correct_c
        context['count_correct_lastweek'] = count_correct_lastweek
        context['count_lastweek'] = count_lastweek

        context['last_using'] = last_using
        context['last_using_str'] = last_using.strftime('%d %b.')  # '%Y.%m.%d'
        context['top3_str'] = top3_str
        context['top3'] = top3
        context['data_list'] = requests
        return context


# unused
class EngListUserView(TemplateView, LoginRequiredMixin):
    template_name = "Eng_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        # todo filter request
        context['data_list'] = EngFixer.objects.filter()
        return context
