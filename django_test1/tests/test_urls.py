from pprint import pprint

from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from eng_service.models import EngFixer, UserProfile
from eng_service.models_core import User


# db
class CreateEngTestBase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create users
        cls.user1 = User.objects.create_user(username='user1')
        cls.user2 = User.objects.create_user(username='user2')
        cls.user3 = User.objects.create_user(username='user3')

        # Create profiles
        cls.profile1 = UserProfile.objects.create(user=cls.user1)
        cls.profile3 = UserProfile.objects.create(user=cls.user3)

        # Create test EngFixer object
        cls.eng1 = EngFixer.objects.create(
            input_sentence='test',
            fixed_sentence='test_fixed_TEST_CREATED',
        )

        # Create test clients
        cls.guest_client = Client()

        # Create authorized test clients
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user1)
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)

    @classmethod
    def tearDownClass(cls):
        EngFixer.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

        super().tearDownClass()

    def setUp(self):
        # Clear cache before each test
        cache.clear()


@override_settings(RATELIMIT_ENABLED=False)
class EngTestURLS(CreateEngTestBase):
    def test_urls(self):
        exmpl_pk = EngFixer.objects.first().pk

        urlpatterns = [('eng_service:eng', None),
                       ('eng_service:eng_get', exmpl_pk),  # EMPTY DB
                       ('eng_service:eng_profile', None),  # PERSONAL PROFILE
                       ('eng_service:eng_list', None),
                       ('eng_service:eng_random', None),  # 302
                       ('signup', None),
                       ('eng_service:api_vset-detail', exmpl_pk),
                       ('eng_service:api_vset-list', None),
                       ('swagger-ui', None),
                       ('page_github', None)
                       ]

        for pattern in urlpatterns:
            print(f'testing url (authorized): {pattern}')
            # url = reverse(pattern.name)
            if pattern[1] is None:
                kwargs = {}
            else:
                kwargs = {'pk': pattern[1]}

            url = reverse(pattern[0], kwargs=kwargs)
            response = self.authorized_client.get(url)  # auth
            # response = self.client.get(url) # anon

            status = response.status_code
            self.assertIn(status, [200, 302], msg=f'info: pattern: {pattern} status: {status}')

    def test_list(self):
        response = self.authorized_client.get(reverse('eng_service:eng_list'))
        self.assertEqual(response.status_code, 200)
        pprint(response.context['data_list'])
        self.assertEqual(response.context['data_list'].count(), 1)

    def test_get_404(self):
        response = self.authorized_client.get(reverse('eng_service:eng_get', kwargs={'pk': 9999}), {})
        self.assertEqual(response.status_code, 404)
