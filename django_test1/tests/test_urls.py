from django import forms
from django.test import TestCase, Client, override_settings
from django.core.cache import cache
from django.urls import reverse

from eng_service.models import EngFixer, UserProfile
from eng_service.models_core import User


# from FORM_MSG.tests.tests_views import MessageTestBase

# db
class CreateEngTestBase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # cls.user = User.objects.get(username='admin')
        cls.eng1 = EngFixer.objects.create(
            input_sentence='test',
            fixed_sentence='test_fixed',
        )
        user3 = User.objects.create_user(username='user3')

        cls.profile1 = UserProfile.objects.create(user=user3)

        # cls.profile2 = UserProfile.objects.create(user=User.objects.get(username='user1'))

# BASE CLASS
class CreateClientsTestBase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # cls.user = User.objects.get(username='admin')
        cls.user = User.objects.create_user(username='user1')
        cls.user2 = User.objects.create_user(username='user2')
        # cls.message = Message.objects.create(author=cls.user,
        #                                      name='Name',
        #                                      text='123')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

        """Создаем клиент зарегистрированного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        cache.clear()


# class SwaggerTest(TestCase):
#     def test_get_page(self):
#         r = self.client.get(reverse('api:openapi-schema'))
#         self.assertEqual(r.status_code, 200)
#
#         r = self.client.get(reverse('api:swagger-ui'))
#         self.assertEqual(r.status_code, 200)


class MessageTestURLS(CreateClientsTestBase,
                      CreateEngTestBase
                      ):

    def test_urls(self):
        """ 'eng_service:eng', 'eng_service:eng_get', 'eng_service:eng_profile', 'eng_service:eng_list',
                       """
        urlpatterns = [('eng_service:eng', None),
                       ('eng_service:eng_get', 1), # EMPTY DB
                       # ('eng_service:eng_profile', 1), # EMPTY DB
                       ('eng_service:eng_list', None),
                       # ('eng_service:eng_random', None), # 302
                       ]

        for pattern in urlpatterns:
            print(f'testing url: {pattern}')
            # url = reverse(pattern.name)
            if pattern[1] is None:
                kwargs = {}
            else:
                kwargs = {'pk': pattern[1]}

            url = reverse(pattern[0], kwargs=kwargs)

            response = self.authorized_client.get(url) # auth
            # response = self.client.get(url) # anon

            self.assertEqual(response.status_code, 200)

    # def test_create_request_auth_123(self):
    #     response = self.authorized_client.get(reverse('eng_service:eng_get', kwargs={}))
    #     print(response)
    #     self.assertEqual(response.status_code, 200)

    def test_create_request_auth(self):
        response = self.authorized_client.post(reverse('eng_service:eng'), {
            'input_sentence': 123,
            # 'user': self.authorized_client
        })
        print(response)
        self.assertEqual(response.status_code, 200)

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

        ###############################

    def test_edit_msg_guest(self):
        """redirect to login"""
        response = self.client.get(reverse('form_msg:edit_msg', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/?next=/'))
        # self.assertEqual(response.url, '/accounts/login/?next=/msg1/edit/1/')

    def test_edit_msg_other_user(self):
        """redirect to login"""
        response = self.authorized_client2.get(reverse('form_msg:edit_msg', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    def test_delete_msg_guest(self):
        response = self.client.get(reverse('form_msg:delete_msg', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/?next=/'))
        # self.assertEqual(response.url, '/accounts/login/?next=/msg1/edit/1/')

    def test_delete_msg_other_user(self):
        response = self.authorized_client2.get(reverse('form_msg:delete_msg', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    def test_delete_msg_by_creator(self):
        response = self.authorized_client.get(reverse('form_msg:delete_msg', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)

# class LikeMessageTestURLS(MessageTestBase):
#     def test_like_msg_auth(self):
#         # MessageTestURLS.test_create_msg_auth()
#
#         response = self.authorized_client.post(reverse('form_msg:like', kwargs={'pk': 1}), {})
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(response.url, reverse('form_msg:msg_list'))
#
#     def test_like_msg_guest(self):
#         response = self.client.post(reverse('form_msg:like', kwargs={'pk': 1}), {})
#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(response.url.startswith('/accounts/login/?next=/'))
#
#     def test_like_msg_404(self):
#         response = self.authorized_client.post(reverse('form_msg:like', kwargs={'pk': 9999}), {})
#         self.assertEqual(response.status_code, 404)
