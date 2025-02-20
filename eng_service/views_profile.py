from datetime import timedelta, datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Now
from django.views.generic import TemplateView

from eng_service.models import Request, EngFixer, UserProfile
from eng_service.service_eng import EngFixParser


def get_user_requests(user):
    return Request.objects.filter(user_profile=user.profile).select_related('fix')


def add_quiz_context(context):
    q = EngFixer.objects.filter(its_correct=False, is_public=True).order_by('?').first()
    if q:
        context.update(dict(quiz=True, random_sentence=q.input_sentence,
                            random_sentence2=q.fixed_sentence, random_sentence_url=q.get_absolute_url()))


class EngProfileView(TemplateView, LoginRequiredMixin):  # FeatureTestMix
    template_name = "Eng_profile.html"

    def get(self, request, *args, **kwargs):
        # redirect login
        # if not self.request.user.is_authenticated:
        #     logging.warning(f'Profile page. User not authenticated: {self.request.user}')
        #     return redirect('login')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            # profile = self.request.user.userprofile
            profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        else:
            # anon filter in get
            profile = None
            context.update(count=0,
                           count_correct=0,
                           count_correct_lastweek=0,
                           count_lastweek=0,
                           last_using_str=datetime.now().strftime('%d %b.'),
                           # top3_str=top_str, top3=top
                           )

            add_quiz_context(context)
            return context

        # STATS FOR USER
        requests = (Request.objects.filter(user_profile=profile)
                    .select_related('fix')
                    # .order_by('-created_date')
                    .values('fix_id', 'fix__its_correct',
                            'fix__fixed_result_JSON',
                            # 'created_date'
                            ).distinct())

        if not requests:
            context.update(dict(count=0, count_correct=0, count_correct_lastweek=0, count_lastweek=0, top3=None,
                                last_using_str=None))
        elif requests:
            count = len(requests)
            # count_correct_c = len([r for r in requests if r['fix__its_correct']]) # v1
            count_correct = Request.objects.filter(user_profile=profile).select_related('fix').filter(
                fix__its_correct=True)
            count_correct_c = count_correct.count()

            last_using = (Request.objects.filter(user_profile=profile).values_list('created_date')
            .order_by('-created_date').first()[0])

            last_week = Now() - timedelta(days=7)
            count_lastweek = requests.filter(created_date__gte=last_week).count()
            count_correct_lastweek = count_correct.filter(created_date__gte=last_week).count()

            top = EngFixParser().parse_multiple_items_top_mistakes(items=requests, top_n=3)
            if top:
                top_str = '\n'.join([f'{item[0]} - {item[1]}' for item in top])
            else:
                top_str = ''

            context.update(count=count,
                           count_correct=count_correct_c,
                           count_correct_lastweek=count_correct_lastweek,
                           count_lastweek=count_lastweek,
                           last_using_str=last_using.strftime('%d %b.'),
                           top3_str=top_str, top3=top)

        context['data_list'] = requests

        add_quiz_context(context)
        return context
