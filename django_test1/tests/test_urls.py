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

        # cls.user = User.objects.get(username='admin')
        cls.eng1 = EngFixer.objects.create(
            input_sentence='test',
            fixed_sentence='test_fixed_TEST_CREATED',
        )
        user3 = User.objects.create_user(username='user3')

        # cls.profile1 = UserProfile.objects.create(user=User.objects.get(username='user1'))
        cls.profile3 = UserProfile.objects.create(user=user3)

# BASE CLASS
class CreateClientsTestBase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user1 = User.objects.create_user(username='user1')
        cls.user2 = User.objects.create_user(username='user2')
        # cls.message = Message.objects.create(author=cls.user,
        #                                      name='Name',
        #                                      text='123')
        cls.profile1 = UserProfile.objects.create(user=User.objects.get(username='user1'))


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

        """Создание клиента зарегистрированного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)

        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        cache.clear()

@override_settings(RATELIMIT_ENABLED=False)
class EngTestURLS(CreateClientsTestBase, CreateEngTestBase):
    def test_urls(self):
        urlpatterns = [('eng_service:eng', None),
                       ('eng_service:eng_get', 1), # EMPTY DB
                       # ('eng_service:eng_profile', 1), # EMPTY DB
                       ('eng_service:eng_list', None),
                       ('eng_service:eng_random', None), # 302
                       ('signup', None),
                       # ('eng_service:api1', None), # post
                       ('eng_service:api_vset-detail', 1),
                       ('eng_service:api_vset-list', None),
                       # ('schema-json', None),
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

            response = self.authorized_client.get(url) # auth
            # response = self.client.get(url) # anon

            status = response.status_code
            self.assertIn(status, [200, 302])

    # def test_create_request_auth_123(self):
    #     response = self.authorized_client.get(reverse('eng_service:eng_get', kwargs={}))
    #     print(response)
    #     self.assertEqual(response.status_code, 200)

    def test_create_invalid_request1(self):
        """Input sentence is too short"""
        response = self.authorized_client.post(reverse('eng_service:eng'), {
            'input_sentence': 123,
            # 'user': self.authorized_client
        })
        self.assertFormError(response.context['form'],'input_sentence', 'Input sentence is too short')

    def test_create_valid_request(self):
        response = self.authorized_client.post(reverse('eng_service:eng'), {
            'input_sentence': 'hello how are you',
        })

        self.assertRedirects(response, reverse('eng_service:eng_get', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 302)
        pprint(response.url)
        self.assertEqual(EngFixer.objects.count(), 2)

        obj = EngFixer.objects.get(pk=2)
        self.assertEqual(obj.its_correct, False)
        self.assertEqual(obj.fixed_sentence, 'Hello how are you')
        # pprint(EngFixer.objects.get(pk=2).__dict__)



    def test_list(self):
        response = self.authorized_client.get(reverse('eng_service:eng_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['data_list'].count(), 1)

    # def test_create_msg_guest(self):
    #     """redirect to login"""
    #     response = self.client.post(reverse('form_msg:send_msg'), {
    #         'name': 123,
    #         'text': 321,
    #         'user': self.client
    #     })
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(response.url.startswith('/accounts/login/?next=/'))
    #     # self.assertEqual(response.url, '/accounts/login/?next=/msg1/send/')

    def test_get_404(self):
        response = self.authorized_client.get(reverse('eng_service:eng_get', kwargs={'pk': 9999}), {})
        self.assertEqual(response.status_code, 404)

