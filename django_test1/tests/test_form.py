from pprint import pprint

from django.test import override_settings
from django.urls import reverse

from django_test1.tests.test_urls import CreateEngTestBase
from eng_service.models import EngFixer


@override_settings(RATELIMIT_ENABLED=False)
class EngTestForm(CreateEngTestBase):
    def test_create_invalid_request1(self):
        """Input sentence is too short"""
        response = self.authorized_client.post(reverse('eng_service:eng'), {
            'input_sentence': 123,
        })
        self.assertFormError(response.context['form'],'input_sentence', 'Input sentence is too short')

    def test_create_valid_request(self):
        response = self.authorized_client.post(reverse('eng_service:eng'), {
            'input_sentence': 'hello how are you',
        })
        redir_pk = EngFixer.objects.last().pk
        self.assertRedirects(response, reverse('eng_service:eng_get', kwargs={'pk': redir_pk}))
        self.assertEqual(response.status_code, 302)

        # pprint(response.url)
        self.assertEqual(EngFixer.objects.count(), 2)

        objs = EngFixer.objects.all()
        pprint(objs)

        obj = EngFixer.objects.get(pk=redir_pk)
        self.assertEqual(obj.its_correct, False)
        self.assertEqual(obj.fixed_sentence, 'Hello how are you')