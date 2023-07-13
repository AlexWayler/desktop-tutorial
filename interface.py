# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import add_account, select_account, engine
from datetime import datetime


class BotInterface():
    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.longpoll = VkLongPoll(self.interface)
        self.params = {}
        self.worksheets = []
        self.offset = 0
        self.keys_user_data = []

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()
                                }
                                )

    # par - отличительный параметр
    def tracking_message(self, par):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if par == 'name':
                    return event.text

                if par == 'sex':
                    if event.text == "1" or event.text == "2":
                        return int(event.text)
                    else:
                        self.message_send(event.user_id, 'Неверный формат ввода пола. Введите 1 или 2:')

                if par == 'city':
                    return event.text

                if par == 'year':
                    return datetime.now().year - int(event.text.split('.')[2])

    def check_data(self, event):
        if self.params['name'] is None:
            self.message_send(event.user_id, 'Введите ваше имя и фамилию')
            return self.tracking_message('name')

        elif self.params['sex'] is None:
            self.message_send(event.user_id, 'Введите свой пол цифрой: 1-м, 2-ж')
            return self.tracking_message('sex')

        elif self.params['city'] is None:
            self.message_send(event.user_id, 'Введите город, в котором проживаете')
            return self.tracking_message('city')

        elif self.params['year'] is None:
            self.message_send(event.user_id, 'Введите дату рождения (дд.мм.гггг):')
            return self.tracking_message('year')

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Здравствуй {self.params["name"]}')

                    # обработка данных, которые не получили
                    self.keys_user_data = self.params.keys()
                    for i in self.keys_user_data:
                        if self.params[i] is None:
                            self.params[i] = self.check_data(event)

                    self.message_send(event.user_id, 'Вы успешно зарегистрировались!')

                elif command == 'поиск':
                    self.message_send(event.user_id, 'Поиск...')
                    # В цикле происходит проверка человека в БД и добавление, если его нет
                    while True:
                        if self.worksheets:
                            worksheet = self.worksheets.pop()
                            if not select_account(engine, event.user_id, worksheet['id']):
                                add_account(engine, event.user_id, worksheet['id'])
                                break
                        else:
                            self.worksheets = self.api.search_worksheet(
                                self.params, self.offset)

                    photos_user = self.api.get_photos(worksheet['id'])
                    self.offset += 10

                    attachment = ''
                    for photo in photos_user:
                        attachment += f'photo{photo["owner_id"]}_{photo["id"]},'

                    self.message_send(event.user_id,
                                      f'Встречайте {worksheet["name"]} ссылка: vk.com/id{worksheet["id"]}',
                                      attachment=attachment
                                      ) 

                elif command == 'пока':
                    self.message_send(event.user_id, 'До свидания!')
                else:
                    self.message_send(event.user_id, 'Команда не опознана')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()

            

