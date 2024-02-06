import json
import logging
import time
from collections import Counter
from typing import Dict, List, Any

import requests
from pprint import pprint

from eng_service.parser_headers_const import headers_engd, headers_eng_rephr


class HttpService:
    # todo download_fixed_data TO general dwnld class
    @staticmethod
    def get_request_post(url: str, headers: dict, params: dict = None, data: dict | str = None):
        try:
            response = requests.post(url, headers=headers, data=data, timeout=5)
            logging.info(f'Request status code: {response.status_code}')

            # response.ok

            if response.status_code == 200:
                result_json = response.json()
                if not result_json:
                    raise Exception('No data from resource')
                return result_json
            else:
                logging.error(f'Request failed with status code: {response.status_code}')
                return

        except Exception as e:
            logging.error(str(e))
            return


class EngDownloader(HttpService):
    def get_data(self, input_str: str = None):
        headers = headers_engd

        # "interfaceLanguage":"ru" OR en
        data = '{"englishDialect":"indifferent","autoReplace":true,"getCorrectionDetails":true,"interfaceLanguage":"ru",' \
               '"locale":"","language":"eng","text":"MY_INPUT","originalText":"","spellingFeedbackOptions":{' \
               '"insertFeedback":true,"userLoggedOn":false},"origin":"interactive","isHtml":false} ' \
            .replace('MY_INPUT', input_str)
        return self.get_request_post(url='https://orthographe.reverso.net/api/v1/Spelling/', headers=headers,
                                     params=None, data=data)


# todo like EngFixParser
class EngRephr:  # inherits HttpEngService?
    def __init__(self, input_str=None):
        self.input_str = input_str

    def parse_data(self):
        pass

    # todo NEW DOWNLOADER AFTER ENG D
    @staticmethod
    def get_data(input_str=None):
        headers = headers_eng_rephr
        params = {
            'language': 'en',
            'sentence': input_str,
            'candidates': '10',
        }

        response = requests.get('https://rephraser-api.reverso.net/v1/rephrase', params=params, headers=headers)
        # pprint(response.json())
        return response.json()

    def get_rephrased_sentences(self, input_str: str = "Today's good weather. I feel good") -> list | None:
        data = self.get_data(input_str)
        data = data.get('candidates')  # feature: order by diversity

        if not data:
            logging.warning('No data: rephraser')
            return None

        sentences = [item['candidate'] for item in data]
        return sentences


# unused tmp
def get_mistakes_data_LANGtool(input_str):
    """https://languagetool.org/insights/post/grammar-dynamic-vs-stative-verbs/"""

    headers = {
        'authority': 'api.languagetool.org',
        'accept': '*/*',
        'accept-language': 'ru',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'dnt': '1',
        'origin': 'https://languagetool.org',
        'referer': 'https://languagetool.org/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    params = {
        'c': '1',
        'instanceId': '85682:1667331050924',
        'v': 'standalone',
    }

    # need escaping
    data = {
        # 'data': '{"text":"We\'ve receive a new proposal for the project. I will keep you informed about how things go."}',
        'data': f'{{"text": "{input_str}"}}',
        'textSessionId': '85682:1667331050924',
        'enableHiddenRules': 'true',
        'level': 'picky',
        'language': 'en-us',
        'disabledRules': 'WHITESPACE_RULE',
        'useragent': 'webextension-chrome-ng',
        'mode': 'all',
        # 'mode': 'allButTextLevelOnly',
        'allowIncompleteResults': 'false',
    }

    response = requests.post('https://api.languagetool.org/v2/check', params=params, headers=headers, data=data)
    logging.info(response.status_code)
    pprint(response.json())
    return response.json()


# todo outd
def download_fixed_data(input_str, response_lang='ru'):
    headers = {
        'authority': 'orthographe.reverso.net',
        'accept': 'text/json',
        'accept-language': 'en',
        'content-type': 'application/*+json',
        'origin': 'https://www.reverso.net',
        'referer': 'https://www.reverso.net/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    # "interfaceLanguage":"ru" OR en
    data = '{"englishDialect":"indifferent","autoReplace":true,"getCorrectionDetails":true,"interfaceLanguage":"ru",' \
           '"locale":"","language":"eng","text":"MY_INPUT","originalText":"","spellingFeedbackOptions":{' \
           '"insertFeedback":true,"userLoggedOn":false},"origin":"interactive","isHtml":false} ' \
        .replace('MY_INPUT', input_str)

    try:
        response = requests.post('https://orthographe.reverso.net/api/v1/Spelling/',
                                 headers=headers, data=data, timeout=5)
        logging.info(f'Fix Request status code: {response.status_code}')

        if response.status_code == 200:
            result_json = response.json()
            if not result_json:
                raise Exception('No data from resource')
            return result_json
        else:
            logging.error(f'Request failed with status code: {response.status_code}')
            return

    except Exception as e:
        logging.error(str(e))
        return


def save_file_TEST(types_list_unique):
    with open('!ENG_TYPES.txt', 'a', encoding='utf-8') as f:
        # json.dump(types_cnt_dict, f, ensure_ascii=False, indent=4)
        f.write(',' + ','.join(types_list_unique))


class EngFixParser:
    def __init__(self, downloader=None):
        if downloader is None:
            self.downloader = EngDownloader()

    def get_parsed_data(self, input_str: str) -> dict:
        """parsing from json.
        See example in ENG_FIX_resp.md"""

        data = self.downloader.get_data(input_str)
        text = data.get("text")
        its_correct = text == input_str

        error_types = []
        corrections_list: list[dict] = []

        corrections_raw = data.get('corrections')
        if corrections_raw:
            for corr in corrections_raw:
                # get by keys from response: mistakes.append({corr['shortDescription'], ...})
                corrections_list.append(
                    {key: corr[key] for key in
                     ['type', 'shortDescription', 'longDescription', 'mistakeText', 'suggestions']})

                error_types.append(corr['type'])

        #  ['grammar', 'punctuation', 'syntax', 'style', 'vocabulary', 'spelling', 'typos']
        valid_types = ('Grammar', 'MisusedWord', 'Punctuation', 'Spelling')

        types_most_value = None
        types_list_unique = None
        if error_types:
            """error_types contains duplicates for counting"""
            types_cnt_dict = Counter(error_types)
            types_list_unique = list(types_cnt_dict.keys())
            types_most_tuple = types_cnt_dict.most_common(1)[0]
            types_most_value = types_most_tuple[0]
            types_most_cnt = types_most_tuple[1]

            # save_file_TEST(types_list_unique)
        result = dict(text=text, corrections=corrections_list, error_types=types_list_unique,
                      types_most=types_most_value, its_correct=its_correct)
        return result

    @staticmethod
    def parse_item_mistakes_V1(item):
        """parse from jsonfield"""
        mistakes = []
        eng_json = item.get('fix__fixed_result_JSON')
        if eng_json:
            for sentence in eng_json:
                if 'type' in sentence:
                    mistakes.append(sentence['type'])
        return mistakes

    @staticmethod
    def parse_multiple_items_top_mistakes(items, top_n):
        mistakes_list = []
        top_mistakes = None

        for i in items:
            parsed_mistakes = EngFixParser.parse_item_mistakes_V1(i)
            if parsed_mistakes:
                mistakes_list.extend(parsed_mistakes)

        if mistakes_list:
            types_cnt_dict = Counter(mistakes_list)
            top_mistakes = types_cnt_dict.most_common(top_n)
        return top_mistakes

    @staticmethod
    def parse_item_mistakes_to_dict(item: dict, top_n: int) -> dict[str, list[Any] | str | Counter[Any]] | dict[str, Any]:
        """
        parse from jsonfield

        :param item: dict
        :param top_n: int
        :return: list of mistakes types
        """

        mistakes_list = []
        eng_item_json = item.get('fix__fixed_result_JSON')
        if eng_item_json:
            for sentence in eng_item_json:
                if 'type' in sentence:
                    mistakes_list.append(sentence['type'])

            if mistakes_list:
                types_cnt_dict = Counter(mistakes_list)
                top_mistakes = types_cnt_dict.most_common(top_n)
                top_mistakes_str = '\n'.join([f'{item[0]} - {item[1]}' for item in top_mistakes])
                return dict(mistakes_list=mistakes_list, top_mistakes=top_mistakes, top_mistakes_str=top_mistakes_str, types_cnt_dict=types_cnt_dict)
            else:
                return dict(mistakes_list=mistakes_list)
        return {}




def time_measure(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(time.perf_counter() - start)
        return result

    return wrapper


@time_measure
def main():
    print(EngRephr().get_rephrased_sentences(input_str='hello im fine. Are you fine?'))


if __name__ == '__main__':
    # 900ms response

    # get_mistakes_data_LANGtool('hello im fine')
    # import time
    # start = time.perf_counter()
    #
    # print(EngRephr().get_rephrased_sentences(input_str='hello im fine'))
    # # fixer(input_str="hello im fine")
    #
    # print(time.perf_counter() - start)

    main()
