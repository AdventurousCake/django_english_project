from pprint import pprint
from unittest import mock

from django.test import override_settings
from django.urls import reverse

from django_test1.tests.test_urls import CreateEngTestBase


def mock_get_data_res(*args, **kwargs):
    input_sentence = 'hello how are you123'
    fixed_sentence = 'Hello how are you123'
    fixed_result_JSON = '[]'
    rephrases_list = []
    translated_input = 'hello how are you'
    translated_fixed = 'Hello how are you'
    types_most = []
    error_types = []
    its_correct = False
    return dict(input_str=input_sentence, fixed_sentence=fixed_sentence, fixed_result_JSON=fixed_result_JSON,
                rephrases_list=rephrases_list, translated_input=translated_input, translated_fixed=translated_fixed,
                types_most=types_most, error_types=error_types, its_correct=its_correct)


@mock.patch("eng_service.utils_.FixerResultProcessor.process_data", mock_get_data_res)
@override_settings(RATELIMIT_ENABLED=False)
class EngTestAPI(CreateEngTestBase):
    def test_api(self):
        response = self.authorized_client.get(reverse('eng_service:api_vset-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_post(self):
        response = self.authorized_client.post(reverse('eng_service:api1'), {"input_sentence": "hello how are you123"})
        pprint(response)
        self.assertEqual(response.status_code, 200)
