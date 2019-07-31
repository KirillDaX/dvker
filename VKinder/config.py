import vk_api
# часть данных VK

age_range = 1
count_find = 10

APP_ID = 6984843
# BASE_URL = 'https://oauth.vk.com/authorize'
# https://oauth.vk.com/authorize?client_id=6984843&redirect_uri=https://oauth.vk.com/blank.html&response_type=token&v=5.101&scope=wall+friends+pages+groups
TOKEN = input('для получения ТОКЕНА: https://oauth.vk.com/authorize?client_id=6984843&redirect_uri=https://oauth.vk.com/blank.html&response_type=token&v=5.101&scope=wall+friends+pages+groups \n Введите токен: ')
# TOKEN = 'static'

simbol_pattern = r'[!@#$%^&*()№±_=\\\|\'\"\-\+\}\{\[\]\<\>\?\/]'

# points system
friends_points = 2
group_points = 1
interests_point = 2
music_points = 1
movies_points = 1

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()


# получем id  из любого ввода
def users_get_id(person):
    response = vk.users.get(user_ids=person)
    return response[0]['id']


target_id = users_get_id(input('введите ID или screen_name пользователя: '))