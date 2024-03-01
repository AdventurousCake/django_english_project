import time

from eng_service.local_lib.google_translate import Translate


class ResultProcessor:
    @staticmethod
    def process_data(input_str):
        from eng_service.service_eng import EngFixParser, EngRephraseParser

        start = time.perf_counter()

        # fix = EngFixParser.get_parsed_data(input_str)
        fix = EngFixParser().get_parsed_data(input_str)
        fixed_result_JSON = fix.get('corrections')
        fixed_sentence = fix.get('text')
        its_correct = fix.get('its_correct')

        # TODO TMP error_types
        error_types = fix.get('error_types')
        types_most = fix.get('types_most')

        # rephraser
        rephrases_list = None
        rephrases = EngRephraseParser().get_parsed_data(input_str=input_str)
        if rephrases:
            rephrases_list = rephrases

        # translate
        TRANSLATE_ENABLED = False
        if TRANSLATE_ENABLED:
            translated_input = Translate().get_ru_from_eng(text=input_str)
            translated_fixed = Translate().get_ru_from_eng(text=fixed_sentence)
        else:
            translated_input, translated_fixed = None, None

        timing = time.perf_counter() - start

        return dict(input_str=input_str, fixed_sentence=fixed_sentence, fixed_result_JSON=fixed_result_JSON,
                    rephrases_list=rephrases_list, translated_input=translated_input, translated_fixed=translated_fixed,
                    types_most=types_most, error_types=error_types, its_correct=its_correct)


class SuggestionsParser:
    """parse suggestions from json"""
    @staticmethod
    def parse_json(json_data: list[dict]):
        """'fixed_result_JSON': [{'longDescription': 'Слово было написано неправильно',
                                        'mistakeText': 'didnt',
                                        'shortDescription': 'Орфографическая ошибка',
                                        'suggestions': [{'category': 'Spelling',
                                                         'definition': 'did not',
                                                         'text': "didn't"}],
                                        'type': 'Spelling'},
                                       {'longDescription': 'Число глагола и подлежащего не '
                                                           'согласованы',
                                        'mistakeText': 'feels',
                                        'shortDescription': 'Грамматическая ошибка',
                                        'suggestions': [{'category': 'Verb', 'text': 'feel'},
                                                        {'category': 'Verb',
                                                         'text': 'am feeling'},
                                                        {'category': 'Verb',
                                                         'text': 'have felt'}],
                                        'type': 'Grammar'}],"""
        suggestions_rows = []
        if json_data:
            for item in list(json_data):
                input_text = item.get('mistakeText')
                long_description = item.get('longDescription')  # gramm mistake
                short_description = item.get('shortDescription')
                suggestions: list[dict] = item.get('suggestions')
                """'suggestions': [{
                                        'text': 'I feel',
                                        'category': 'Verb'
                                    },
                                    {
                                        'text': "I'm feel",
                                        'category': 'Spelling'
                                    },],"""

                fixed_text = ""
                sugg_string = ""
                if suggestions:
                    fixed_text = suggestions[0]['text']  # TEXT from first suggestion
                    sugg_string = '\n'.join(
                        f"{s['text']} ({s['category']}, {s.get('definition', '')})" for s in suggestions)

                suggestions_rows.append((input_text, fixed_text, long_description, short_description, sugg_string))
        return suggestions_rows


def save_file_TEST(types_list_unique):
    with open('!ENG_TYPES.txt', 'a', encoding='utf-8') as f:
        # json.dump(types_cnt_dict, f, ensure_ascii=False, indent=4)
        f.write(',' + ','.join(types_list_unique))


def time_measure(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(time.perf_counter() - start)
        return result
    return wrapper
