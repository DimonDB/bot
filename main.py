from config import user_token, community_token, offset, line
import vk_api
import requests
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from database import *


class VKBot:
    def __init__(self):
        print('Bot was created')
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)

    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7)})

    def name(self, user_id):
        url = 'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_dict = response['response']
            for i in information_dict:
                for key, value in i.items():
                    return i.get('first_name')
        except KeyError:
            self.write_msg(user_id, 'Введите токен')

    def get_sex(self, user_id):
        url = 'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'sex',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_list = response['response']
            for i in information_list:
                if i.get('sex') == 2:
                    return 1
                elif i.get('sex') == 1:
                    return 2
        except KeyError:
            self.write_msg(user_id, 'Введите токен')

    def get_age_low(self, user_id):
        url = 'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'bdate',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_list = response['response']
            for i in information_list:
                date = i.get('bdate')
            date_list = date.split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(date_list) == 2 or date not in information_list:
                self.write_msg(user_id, 'Введите нижний порог возраста (min - 16): ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        return event.text
        except KeyError:
            self.write_msg(user_id, 'Введите токен')

    def get_age_high(self, user_id):
        url = 'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'bdate',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_list = response['response']
            for i in information_list:
                date = i.get('bdate')
            date_list = date.split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(date_list) == 2 or date not in information_list:
                self.write_msg(user_id, 'Введите верхний порог возраста (max - 80): ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        return event.text
        except KeyError:
            self.write_msg(user_id, 'Введите токен')

    def cities(self, user_id, city_name):
        url = 'https://api.vk.com/method/database.getCities'
        params = {'access_token': user_token,
                  'country_id': 1,
                  'q': f'{city_name}',
                  'need_all': 0,
                  'count': 1000,
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_list = response['response']
            list_cities = information_list['items']
            for i in list_cities:
                found_city_name = i.get('title')
                if found_city_name == city_name:
                    found_city_id = i.get('id')
                    return int(found_city_id)
        except KeyError:
            self.write_msg(user_id, 'Введите токен')

    def find_city(self, user_id):
        url = 'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'fields': 'city',
                  'user_ids': user_id,
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_dict = response['response']
            for i in information_dict:
                if 'city' in i:
                    city = i.get('city')
                    return str(city.get('id'))
                else:
                    self.write_msg(user_id, 'Введите название вашего города: ')
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            city_name = event.text
                            id_city = self.cities(user_id, city_name)
                            return str(id_city)
        except KeyError:
            self.write_msg(user_id, 'Введите токен')

    def find_user(self, user_id):
        url = 'https://api.vk.com/method/users.search'
        params = {'access_token': user_token,
                  'v': '5.131',
                  'sex': self.get_sex(user_id),
                  'age_from': self.get_age_low(user_id),
                  'age_to': self.get_age_high(user_id),
                  'city': self.find_city(user_id),
                  'fields': 'is_closed, id, first_name, last_name',
                  'status': '1' or '6',
                  'count': 500}
        resp = requests.get(url, params=params)
        resp_json = resp.json()
        try:
            dict_1 = resp_json['response']
            list_1 = dict_1['items']
            for person_dict in list_1:
                if person_dict.get('is_closed') != False:
                    continue
                first_name = person_dict.get('first_name')
                last_name = person_dict.get('last_name')
                vk_id = str(person_dict.get('id'))
                vk_link = 'vk.com/id' + str(person_dict.get('id'))
                insert_data_users(id_user)
            return 'Поиск завершён'
        except KeyError:
            self.write_msg(user_id, 'Введите токен')

    def get_photos_id(self, user_id):
        url = 'https://api.vk.com/method/photos.getAll'
        params = {'access_token': user_token,
                  'type': 'album',
                  'owner_id': user_id,
                  'extended': 1,
                  'count': 25,
                  'v': '5.131'}
        resp = requests.get(url, params=params)
        dict_photos = {}
        resp_json = resp.json()
        try:
            dict_1 = resp_json['response']
            list_1 = dict_1['items']
            for i in list_1:
                photo_id = str(i.get('id'))
                i_likes = i.get('likes')
                if i_likes.get('count'):
                    likes = i_likes.get('count')
                    dict_photos[likes] = photo_id
            return sorted(dict_photos.items(), reverse=True)
        except KeyError:
            self.write_msg(user_id, 'Введите токен')

    def get_photo_1(self, user_id):
        list = self.get_photos_id(user_id)
        for count, i in enumerate(list, start=1):
            if count == 1:
                return i[1]

    def get_photo_2(self, user_id):
        list = self.get_photos_id(user_id)
        for count, i in enumerate(list, start=1):
            if count == 2:
                return i[1]

    def get_photo_3(self, user_id):
        list = self.get_photos_id(user_id)
        for count, i in enumerate(list, start=1):
            if count == 3:
                return i[1]

    def send_photo_1(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': user_token,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(offset)}_{self.get_photo_1(self.person_id(offset))}',
                                         'random_id': 0})

    def send_photo_2(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': user_token,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(offset)}_{self.get_photo_2(self.person_id(offset))}',
                                         'random_id': 0})

    def send_photo_3(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': user_token,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(offset)}_{self.get_photo_3(self.person_id(offset))}',
                                         'random_id': 0})

    def find_persons(self, user_id, offset):
        self.write_msg(user_id, self.found_person_info(offset))
        self.person_id(offset)
        insert_data_profiles(self.person_id(offset), offset)
        self.get_photos_id(self.person_id(offset))
        self.send_photo_1(user_id, 'Фото номер 1', offset)
        if self.get_photo_2(self.person_id(offset)) != None:
            self.send_photo_2(user_id, 'Фото номер 2', offset)
            self.send_photo_3(user_id, 'Фото номер 3', offset)
        else:
            self.write_msg(user_id, 'Фотографий больше нет')

    def found_person_info(self, offset):
        tuple_person = select(offset)
        list_person = []
        list_person.extend(iter(tuple_person))
        return f'{list_person[0]} {list_person[1]}, ссылка - {list_person[3]}'

    def person_id(self, offset):
        tuple_person = select(offset)
        list_person = []
        list_person.extend(iter(tuple_person))
        return str(list_person[2])


bot = VKBot() 
