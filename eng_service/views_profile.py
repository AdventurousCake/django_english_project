from collections import Counter

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from eng_service.models import Request, EngFixer
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

# unused
class EngListUserView(TemplateView, LoginRequiredMixin):
    template_name = "Eng_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        # todo filter request
        context['data_list'] = EngFixer.objects.filter()
        return context
