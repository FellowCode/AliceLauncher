import random
from Server.phrases import Phrases

class AliceClient:
    def __init__(self, user_id):
        self.user_id = user_id

    def handle_dialog(self, req, res):
        self.req = req
        self.res = res
        if req['session']['new']:
            # Это новый пользователь.
            self.new_session()
            return

        return res

    def new_session(self):
        # Инициализируем сессию и поприветствуем его.
        self.suggests = {
            'suggests': [
                "Помощь",
                "Выключить экран",
                "Звук потише",
                "Звук погромче",
            ]
        }
        start_phrase = random.choice(Phrases.start_dialog)
        self.res['response']['text'] = start_phrase.text
        if start_phrase.tts:
            self.res['response']['tts'] = start_phrase.tts
        self.res['response']['buttons'] = self.get_suggests()

    def continue_session(self):
        # Обрабатываем ответ пользователя.
        if self.req['request']['original_utterance'].lower() in [
            'ладно',
            'куплю',
            'покупаю',
            'хорошо',
        ]:
            # Пользователь согласился, прощаемся.
            self.res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
            return

        # Если нет, то убеждаем его купить слона!
        self.res['response']['text'] = 'Все говорят "%s", а ты купи слона!' % (
            self.req['request']['original_utterance']
        )
        self.res['response']['buttons'] = self.get_suggests()

    def get_suggests(self):

        # Выбираем две первые подсказки из массива.
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in self.suggests[:2]
        ]

        # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
        self.suggests = self.suggests[1:]

        # Если осталась только одна подсказка, предлагаем подсказку
        # со ссылкой на Яндекс.Маркет.
        if len(suggests) < 2:
            suggests.append({
                "title": "Ладно",
                "url": "https://market.yandex.ru/search?text=слон",
                "hide": True
            })
        return suggests
