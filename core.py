from datetime import datetime

import vk_api

from vk_api.exceptions import ApiError
from config import acces_token


class VkTools():
    def __init__(self, acces_token):
        self.vkapi = vk_api.VkApi(token=acces_token)

    def _bdate_toyear(self, bdate):
        user_year = bdate.split('.')[2]
        now = datetime.now().year
        return now - int(user_year)

    def get_profile_info(self, user_id):

        try:
            info, = self.vkapi.method('users.get',
                                      {'user_id': user_id,
                                       'fields': 'city,sex,relation,bdate'
                                       }
                                      )
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        result = {'name': (info['first_name'] + ' ' + info['last_name']) if
        'first_name' in info and 'last_name' in info else None,
                  'sex': info.get('sex'),
                  'city': info.get('city')['title'] if info.get('city') is not None else None,
                  'year': self._bdate_toyear(info.get('bdate')) if info.get('bdate') is not None else None
                  }
        return result

    def search_worksheet(self, params, offset):

        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = params['year']
        age = curent_year - user_year
        age_from = age - 3
        age_to = age + 3

        users = self.vkapi.method('users.search',
                                  {'count': 10,
                                   'offset': offset,
                                   'age_from': age_from,
                                   'age_to': age_to,
                                   'sex': sex,
                                   'hometown': city,
                                   'status': 6,
                                   'is_closed': False
                                   }
                                  )
        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            if user['is_closed'] == False:
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                            }
                           )

        return res

    def get_photos(self, user_id):
        photos = self.vkapi.method('photos.get',
                                   {'user_id': user_id,
                                    'album_id': 'profile',
                                    'extended': 1
                                    }
                                   )
        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )

        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)
        return res[:3]


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(789657038)
    users = bot.serch_users(params, 20)


