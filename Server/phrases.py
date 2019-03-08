from collections import namedtuple

class Phrases:
    #Определяем именованный кортеж
    Phrase = namedtuple('Phrase', 'text tts')
    # набор фраз формата (Текст, tts)
    start_dialog = [Phrase('Привет! Что желете?', None),
                    Phrase('Привет, ваши пожелания?', None)]

    start_no_sync = [Phrase('Привет! Лаунчер не синхронизирован с этим устройством.\n'
                      'Для начала процесса синхронизации скажите синхронизация.', None)]

    start_app_no_enable = [Phrase('Привет! Запусти лаунчер, не могу достучаться до него.\n', None)]
