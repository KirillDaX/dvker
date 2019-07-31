from datetime import datetime
import db_module
import re
import vk_api
import config

new_offset = db_module.count_offset()
data_user = {}

vk_session = vk_api.VkApi(token=config.TOKEN)
vk = vk_session.get_api()


def get_user_info(user_id_target):
    """получаем базовое инфо о пользователе в формате:
    [{'id': int, 'first_name': 'str', 'last_name': 'str', 'is_closed': True, 'can_access_closed': True}]"""
    # поля необходимые  для сравнения
    fields_param = 'bdate', 'books', 'city', 'country', 'sex', 'interests', 'music ', 'movies ', 'relation'
    response2 = vk.users.get(user_ids=user_id_target, fields=fields_param)  # Используем метод users.get
    try:
        # прмерный возраст
        data_user['age'] = int((datetime.now() - datetime.strptime(response2[0]['bdate'], '%d.%m.%Y')).days / 365)
        data_user['books'] = response2[0]['books']
        data_user['interests'] = response2[0]['interests']
        data_user['music'] = response2[0]['music']
        # data_user['groups'] = response2[0]['groups']\
        data_user['sex'] = response2[0]['sex']
        data_user['city'] = response2[0]['city']
    except ValueError:
        print('--')
    except KeyError:
        data_user['city'] = {'id': None}
        return data_user


def search_module(count_limit):
    """проводим поиск по основным характеристикам, возвращает список ids_list"""
    data_for_search = get_user_info(config.target_id)
    fields_param = 'bdate', 'books', 'city', 'country', 'sex', 'interests', 'music ', 'movies ', 'relation'
    try:
        if data_for_search['sex'] != 0:
            if data_for_search['sex'] == 1:
                data_for_search['sex_need'] = 2
            else:
                data_for_search['sex_need'] = 1
        else:
            data_for_search['sex_need'] = int(input('Выберете кого ищем? 1 = Ж, 2 = М :'))
    except KeyError:
        data_for_search['sex_need'] = int(input('Не указан пол, Выберете кого ищем? 1 = Ж, 2 = М'))
    try:
        data_for_search['age'] == True
    except KeyError as about_error:
        if 'age' in about_error.__str__():
            data_user['age'] = int(input('не указан возраст, введите возарст: '))

    response = vk.users.search(count=count_limit,
                               city=data_for_search['city']['id'],
                               sex=data_for_search['sex_need'],
                               age_from=data_for_search['age'] - config.age_range,
                               age_to=data_for_search['age'] + config.age_range,
                               fields=fields_param,
                               offset=new_offset)

    ids_list = [item['id'] for item in response['items']]
    print('search_module = done \n')
    return ids_list


def get_common_friends(for_who, list_with_ids):
    """ иищем общих друзей цели и тех id что мы получили из поиска.
    используется friends.getMutual """
    people_with_common_friends = []
    status_index = 1

    for item in list_with_ids:
        try:
            # Выдает ошибку [30] This profile is private, если профиль закрыт.
            response_friends = vk.friends.getMutual(source_uid=for_who, target_uid=item)
            print(f'- now get common friends with = {item} status {status_index} / {len(list_with_ids)}')
            status_index += 1
        except vk_api.exceptions.ApiError as except_info:
            status_index += 1
            print(except_info)
        else:
            if response_friends:
                people_with_common_friends.append({'id': item, 'общих друзей': len(response_friends)})
    print('get_common_friends = done \n')
    return people_with_common_friends


def common_groups(target_id, data_with_ids):
    """находим общие группы"""
    target_groups = vk.groups.get(user_id=target_id)
    candidate_groups = []
    ppl_common_friends_and_groups = []
    show_index = 1
    for item in data_with_ids:
        response_groups = vk.groups.get(user_id=item['id'])
        candidate_groups.append({'id': item['id'], 'groups': response_groups['items']})
        common_groups_id = len(list(set(response_groups['items']) & set(target_groups['items'])))
        ppl_common_friends_and_groups.append({'id': item['id'], 'общих групп': common_groups_id})
        print(f' = work do common_groups {show_index}/{len(data_with_ids)}')
        show_index += 1
    return ppl_common_friends_and_groups


def get_common_interests(target_id, candidates):
    target_info = get_user_info(target_id)
    try:
        target_info['interests'] == True
    except KeyError as about_error:
        if 'interests' in about_error.__str__():
            target_info['interests'] = input('Не указаны интересы, укажите интересы: ')
    pattern = re.sub(config.simbol_pattern, '', target_info['interests']).lower().replace(', ', '|')
    for item in candidates:
        candidates_interests = get_user_info(item['id'])
        common_interests = re.findall(pattern, candidates_interests['interests'].lower())
        if common_interests and '' not in common_interests:
            item['rating'] += config.interests_point


def get_common_music(target_id, candidates):
    target_info = get_user_info(target_id)
    try:
        target_info['music'] == True
    except KeyError as about_error:
        if 'music' in about_error.__str__():
            target_info['music'] = input('Не указа музыка, музыкальные предпочтения: ')
    pattern = re.sub(config.simbol_pattern, '', target_info['music']).lower().replace(', ', '|')
    for item in candidates:
        candidates_interests = get_user_info(item['id'])
        common_interests = re.findall(pattern, candidates_interests['music'].lower())
        if common_interests and '' not in common_interests:
            item['rating'] += config.music_points


def get_photos_top(target_id):
    try:
        photos = vk.photos.get(owner_id=target_id, album_id='profile', extended=1)
    except KeyError as info_about:
        print(info_about)
    return photos['items']


def get_top3_photos(photos_list):
    profile_photos = dict()
    for photo in photos_list:
        profile_photos[photo['id']] = [photo['likes']['count'], photo['sizes'][-1]['url']]
    profile_photos_sorted = sorted(profile_photos.items(), key=lambda x: x[1][0], reverse=True)
    profile_photos_list = profile_photos_sorted[:3]
    profile_id_photos = dict()
    for photo in profile_photos_list:
        profile_id_photos[str(photo[0])] = photo[1][1]
    return profile_id_photos


def update_data_groups_info(main_data, dict_update):
    i = 0
    for item in main_data:
        item.update(dict_update[i])
        i += 1


def prepare_to_db(common_data):
    for item in common_data:
        base_rating = item['общих друзей'] * config.friends_points + item['общих групп'] * config.group_points
        item['rating'] = base_rating
        item['vk_link'] = 'https://vk.com/id' + str(item['id'])
        item['photos'] = get_top3_photos(get_photos_top(item['id']))
