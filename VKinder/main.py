# -*- coding: utf-8 -*-
import function_module
import config
import db_module

""" Описание:

запись происходит в файл result.json"""


if __name__ == '__main__':
    # ===  RUN ===
    # полукчение данных
    def run_all():
        # function_module.users_get_id(config.target_user)
        common_data = function_module.get_common_friends(config.target_id,
                                                         function_module.search_module(config.count_find))
        common_groups_dct = function_module.common_groups(config.target_id, common_data)
        # --------нормализация данных ------------
        function_module.update_data_groups_info(common_data, common_groups_dct)
        # проверка интересов и прочего
        function_module.get_common_interests(config.target_id, common_data)
        # function_module.get_common_music(config.target_id, common_data)
        function_module.prepare_to_db(common_data)  # переобразование данных в конечный вид
        return common_data

    # добавление всего в базу, соритровка по рейтнигу  и внесение в JSON 10 топовых
    db_module.add_all_to_db(run_all())
    db_module.sort_rating_and_write_to_json_file()