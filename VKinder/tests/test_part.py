import unittest
import random
import function_module
import db_module


class MyTestCase(unittest.TestCase):
    def test_search_is_not_empty(self):
        self.result = function_module.search_module(10)
        self.assertNotEqual(len(self.result), 0, 'search data empty')

    def test_user_info(self):
        """ провреяем наличе данных get_user_info на случаййном пользователе"""
        user = random.randint(10000, 6000000)
        self.some_result = function_module.get_user_info(user)
        self.assertNotEqual(len(self.some_result), 0, 'no data from get_user_info')

    def test_db_some_data(self):
        """проверка что в базе что-то есть"""
        for self.data in db_module.vk_collection.find().skip(1).limit(2):
            self.assertNotEqual(len(self.data), 0, 'db_data empty')


if __name__ == '__main__':
    unittest.main()
