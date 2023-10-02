# v1
# import translators as ts
# q_text = 'hi'
# ts.preaccelerate()  # Optional. Caching sessions in advance, which can help improve access speed.
# print(ts.translators_pool)
# print(ts.translate_text(q_text, translator='yandex', to_language='ru'))



# v2
# translator = google_translator()
# translate_text = translator.translate('привет', lang_tgt='en')
# print(translate_text)
from eng_service.local_lib.main import google_translator


class T():
    def __init__(self):
        self.translator = google_translator()

    def get_translate(self, text, target='ru'):
        translate_text = self.translator.translate(text, lang_tgt=target)
        return translate_text

    def get_eng_from_ru(self, text):
        return self.get_translate(text, target='en')

    def get_ru_from_eng(self, text):
        return self.get_translate(text, target='ru')


if __name__ == '__main__':
    import time

    start = time.perf_counter()
    print(T().get_ru_from_eng(text="""hello"""))
    print(time.perf_counter() - start)
