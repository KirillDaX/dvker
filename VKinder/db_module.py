import json
import config
from bson import json_util
from pymongo import MongoClient

client = MongoClient()

db = client['vk_task']
vk_collection = db['vk_base']
starts_collection = db['starts_count']
start_dict = {'starts': 0}


def add_in_db(collection, dict_data):
    what_add = dict_data
    return collection.insert_one(what_add).inserted_id


def sort_rating_and_write_to_json_file():
    result = vk_collection.find().sort('rating', -1)
    for_json_data = {}
    with open("result.json", "w", encoding='utf-8') as write_file:
        for item in result[0:10]:
            for_json_data.update({'vk_account': item['vk_link']})
            for_json_data.update({'top3_photo': item['photos']})
            json.dump(for_json_data, write_file, indent=4, default=json_util.default)
    return result


def count_offset():
    add_in_db(starts_collection, start_dict)
    offset = config.count_find * starts_collection.count()
    if offset > 3000000:
        starts_collection.drop_collection('starts')
        offset = 0
    return offset


def add_all_to_db(data):
    for item in data:
        add_in_db(vk_collection, item)

