import json
import logging
import time
from collections import Counter

import requests
from pprint import pprint


class HttpService:
    # todo download_fixed_data TO general dwnld class
    @staticmethod
    def get_request_POST(url, headers, params=None, data=None):
        try:
            response = requests.post(url, headers=headers, data=data, timeout=5)
            logging.info(f'Request status code: {response.status_code}')

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
    def get_data(self, input_str=None):
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

        # todo input escaping \'
        # data = {"englishDialect": "indifferent", "autoReplace": True, "getCorrectionDetails": True,
        #         "interfaceLanguage": "en", "locale": "", "language": "eng", "text": f"{input_str}",
        #         "originalText": "",
        #         "spellingFeedbackOptions": {"insertFeedback": True, "userLoggedOn": False}, "origin": "interactive",
        #         "isHtml": False}
        #
        # x = json.dumps(data)
        # data = "'" + x + "'"

        # todo INPUT
        # input_str = input_str

        # "interfaceLanguage":"ru" OR en
        data = '{"englishDialect":"indifferent","autoReplace":true,"getCorrectionDetails":true,"interfaceLanguage":"ru",' \
               '"locale":"","language":"eng","text":"MY_INPUT","originalText":"","spellingFeedbackOptions":{' \
               '"insertFeedback":true,"userLoggedOn":false},"origin":"interactive","isHtml":false} ' \
            .replace('MY_INPUT', input_str)
        return self.get_request_POST(url='https://orthographe.reverso.net/api/v1/Spelling/', headers=headers, params=None, data=data)


# todo like EngFixParser
class EngRephr:  # inherits HttpEngService?
    def __init__(self, input_str=None):
        self.input_str = input_str

    def parse_data(self):
        pass

    # todo NEW DOWNLOADER AFTER ENG D
    @staticmethod
    def get_data(input_str=None):
        headers = {
            'authority': 'rephraser-api.reverso.net',
            'accept': 'application/json',
            'accept-language': 'ru,en-US;q=0.9,en;q=0.8',
            'dnt': '1',
            'origin': 'https://www.reverso.net',
            'referer': 'https://www.reverso.net/',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'x-reverso-origin': 'speller.web',
        }

        params = {
            'language': 'en',
            'sentence': input_str,
            'candidates': '10',
        }

        response = requests.get('https://rephraser-api.reverso.net/v1/rephrase', params=params, headers=headers)
        # pprint(response.json())
        return response.json()

    def get_rephrased_sentences(self, input_str="Today's good weather. I feel good"):
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

    # todo input escaping \'
    # data = {"englishDialect": "indifferent", "autoReplace": True, "getCorrectionDetails": True,
    #         "interfaceLanguage": "en", "locale": "", "language": "eng", "text": f"{input_str}",
    #         "originalText": "",
    #         "spellingFeedbackOptions": {"insertFeedback": True, "userLoggedOn": False}, "origin": "interactive",
    #         "isHtml": False}
    #
    # x = json.dumps(data)
    # data = "'" + x + "'"

    # "interfaceLanguage":"ru" OR en
    data = '{"englishDialect":"indifferent","autoReplace":true,"getCorrectionDetails":true,"interfaceLanguage":"ru",' \
           '"locale":"","language":"eng","text":"MY_INPUT","originalText":"","spellingFeedbackOptions":{' \
           '"insertFeedback":true,"userLoggedOn":false},"origin":"interactive","isHtml":false} ' \
        .replace('MY_INPUT', input_str)

    try:
        response = requests.post('https://orthographe.reverso.net/api/v1/Spelling/', headers=headers, data=data,
                                 timeout=5)
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
        # self.downloader = downloader
        if downloader is None:
            self.downloader = EngDownloader()

    # @staticmethod
    def get_parsed_data(self, input_str):
        """parsing from json. Example in ENG_FIX_resp.md"""

        # data = download_fixed_data(input_str)
        data = self.downloader.get_data(input_str)

        text = data.get("text")
        its_correct = text == input_str

        error_types = []
        corrections_list: list[dict] = []

        corrections_raw = data.get('corrections')
        if corrections_raw:
            for corr in corrections_raw:
                # get by keys from response
                # mistakes.append({corr['shortDescription'], corr['longDescription'], corr['correctionText'], ...})
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
            # for i in error_types:
            #     if i in known_types:
            #         pass

            types_cnt_dict = Counter(error_types)
            types_list_unique = list(types_cnt_dict.keys())
            types_most_tuple = types_cnt_dict.most_common(1)[0]
            types_most_value = types_most_tuple[0]
            types_most_cnt = types_most_tuple[1]

            # TODO TMP file
            save_file_TEST(types_list_unique)

        result = dict(text=text, corrections=corrections_list, error_types=types_list_unique,
                      types_most=types_most_value, its_correct=its_correct)

        # print(input_str, result, sep="\n")
        return result


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
