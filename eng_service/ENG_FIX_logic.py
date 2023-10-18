import json

import requests
from pprint import pprint

class EngRephr():
    def __init__(self, input_str=None):
        self.input_str = input_str

    @staticmethod
    def get_rephrased_raw(input_str=None):
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
            'candidates': '10',  # 6
        }

        response = requests.get('https://rephraser-api.reverso.net/v1/rephrase', params=params, headers=headers)
        # pprint(response.json())
        return response.json()

    def get_rephrased_sentences(self, input_str="Today's good weather. I feel good"):
        data = self.get_rephrased_raw(input_str)
        data = data.get('candidates')  # feature: order by diversity
        sentences = [item['candidate'] for item in data]
        return sentences

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

    # todo escaping
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
    print(response.status_code)
    pprint(response.json())
    return response.json()


def get_fixed(input_str, response_lang='ru'):
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

    response = requests.post('https://orthographe.reverso.net/api/v1/Spelling/', headers=headers, data=data)
    return response.json()


def fixer(input_str=None):
    # mstk = get_mistakes_data(input_str)  # languagetool
    # https://translate.yandex.ru/dictionary/%D0%90%D0%BD%D0%B3%D0%BB%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B9-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9/today's

    v2 = get_fixed(input_str)
    # result = v2.get("text")

    # TODO REMOVE; todo check none; simple types
    error_types = []

    mistakes = []
    corrs = v2.get('corrections')  # todo MANY

    for c in corrs:
        # mistakes.append({c['shortDescription'], c['longDescription'], c['correctionText'], c['correctionDefinition'],
        #                  c['suggestions']})

        # get by keys from response
        mistakes.append(
            {k: c[k] for k in ['type', 'shortDescription', 'longDescription', 'mistakeText', 'suggestions']})

        error_types.append(c['type'])

    # corrections
    """[ { 'longDescription': 'A word was not spelled correctly',
        'mistakeText': 'i',
        'shortDescription': 'Spelling Mistake',
        'suggestions': [ { 'category': 'Spelling',
        'definition': 'refers to the speaker or writer',
        'text': 'I'}]},
        
        { 'longDescription': 'Unknown word - no suggestions available',
        'mistakeText': 'django',
        'shortDescription': 'Possible Spelling Mistake',
        'suggestions': []},
    """

    # full resp
    """x = {'id': '8710fb7c-97a8-4545-bd9d-f3b90f33a6e4', 'language': 'eng',
         'text': "We'vereceivedanewproposalfortheproject.Iwillkeepyouinformedabouthowthingsgo.",
         'engine': 'Ginger', 'truncated': False, 'timeTaken': 473, 
         
         'corrections': [
            {'group': 'AutoCorrected', 'type': 'Grammar', 'shortDescription': 'GrammarMistake',
             'longDescription': 'Errorinformingorapplyingthepresentperfecttense', 'startIndex': 0, 'endIndex': 12,
             'mistakeText': "We'vereceive", 'correctionText': "We'vereceived",
             'suggestions': [{'text': "We'vereceived", 'category': 'Verb'}]}],
             
         'sentences': [{'startIndex': 0, 'endIndex': 44, 'status': 'Corrected'},
                       {'startIndex': 46, 'endIndex': 90, 'status': 'Corrected'}], 'autoReplacements': [],
         'stats': {'textLength': 91, 'wordCount': 18, 'sentenceCount': 2, 'longestSentence': 45}}"""


    # result = {"text": v2.get("text"), 'corrections': mistakes, 'error_types': error_types}
    result = dict(text=v2.get("text"), corrections = mistakes, error_types=error_types)

    print(input_str, result, sep="\n")
    print()
    # pprint.pp(mstk)
    # print()
    pprint(v2)

    return result


if __name__ == '__main__':
    # 900ms response

    # get_mistakes_data_LANGtool(
    #     'Today i learn more about django and study 8 hour. Im feel good. Today good weather. have nice day')

    import time
    start = time.perf_counter()

    print(EngRephr().get_rephrased_sentences(input_str='hello im fine'))
    # fixer(input_str="Today i learn more about django. Im feel good. Today good weather. And tomorrow will be better.")

    print(time.perf_counter() - start)


