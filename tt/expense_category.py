# from db_impl_base import DBImplBase
import random
import yaml

from loguru import logger
import mariadb

from db_connection import DBConnection
from db_impl_base import DBImplBase


class ExpenseCategory():

    def __init__(self):
        self.user_identifier = None
        self.uuid = None
        self.name = None


class ExpenseCategoryDBImpl(DBImplBase):

    def __init__(self, db_connection: DBConnection):
        super().__init__(db_connection)

    def get_all(self) -> list[ExpenseCategory]:
        list_of_expense_category_ir = []
        cur = self.db_connection.cur()
        sql_string = 'SELECT user_identifier, uuid, name FROM expense_category;'
        logger.info(sql_string)
        cur.execute(sql_string)
        for (user_identifier, uuid, name) in cur:
            e = ExpenseCategory()
            e.user_identifier = user_identifier
            e.uuid = uuid
            e.name = name
            list_of_expense_category.append(t)
        return list_of_expense_category

    def create_table(self) -> bool:
        cur = self.db_connection.cur()
        sql_string = 'CREATE TABLE IF NOT EXISTS expense_category(\n' \
            'user_identifier varchar(128) not null,\n'\
            'uuid varchar(128) not null,\n'\
            'name varchar(128) not null\n'\
            ')\n' \
            'CHARACTER SET \'utf8\';'
        logger.info(sql_string)
        try:
            cur.execute(sql_string)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)
            return False
        return True

    def start_using_database(self) -> bool:
        cur = self.db_connection.cur()
        sql_string = 'use finance;'
        try:
            cur.execute(sql_string)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)
            return False
        return True

    def get_all_filtered_by_user_identifier(self, user_identifier: str) -> list[ExpenseCategory]:
        cur = self.db_connection.cur()
        escaped_user_identifier = self.escape_sql_string(user_identifier)
        sql_string = f'SELECT user_identifier, uuid, name FROM expense_category WHERE user_identifier={escaped_user_identifier}'
        logger.info(sql_string)
        list_of_expense_category = []
        try:
            cur.execute(sql_string)
            for (user_identifier, uuid, name) in cur:
                expense_category = ExpenseCategory()
                expense_category.user_identifier = user_identifier
                expense_category.uuid = uuid
                expense_category.name = name
                list_of_expense_category.append(expense_category)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)
            return None
        return list_of_expense_category

    def insert_records(self, list_of_category: list[ExpenseCategory]) -> bool:
        cur = self.db_connection.cur()
        for item in list_of_category:
            escaped_user_identifier = self.escape_sql_string(item.user_identifier)
            escaped_uuid = self.escape_sql_string(item.uuid)
            escaped_name = self.escape_sql_string(item.name)
            sql_string = f'INSERT INTO expense_category (user_identifier, uuid, name) VALUES({escaped_user_identifier}, {escaped_uuid}, {escaped_name})'
            logger.info(sql_string)
            try:
                cur.execute(sql_string)
            except mariadb.Error as e:
                self.handle_general_sql_execution_error(e, sql_string)
                return FAlse
        return True

    def drop_table(self) -> bool:
        cur = self.db_connection.cur()
        sql_string = 'DROP TABLE expense_category;'
        logger.info(sql_string)
        try:
            cur.execute(sql_string)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)
            return False
        return True


class ExpenseCategoryControl():

    def __init__(self, db_connection: DBConnection):
        self.db_impl = ExpenseCategoryDBImpl(db_connection)

    def create_or_update(self, category_config_file_path: str) -> bool:

        if not self.db_impl.start_using_database():
            return False
        if not self.db_impl.create_table():
            return False

        category_config = self._build_category_config(category_config_file_path)
        for item in category_config:
            user_identifier = item['user_identifier']
            existing_list_of_category = self.db_impl.get_all_filtered_by_user_identifier(user_identifier)
            list_of_records_to_insert = self._get_list_of_records_to_insert(user_identifier, existing_list_of_category, item['categories'])
            if len(list_of_records_to_insert) > 0:
                self.db_impl.insert_records(list_of_records_to_insert)
        return True

    def delete(self) -> bool:
        if not self.db_impl.start_using_database():
            return False
        return self.db_impl.drop_table()

    def _get_list_of_records_to_insert(self, user_identifier: str, source0: list[ExpenseCategory], source1: list[ExpenseCategory]) -> list[str]:
        existing_uuid_set = self._get_existing_uuid_set(user_identifier)
        # @FIXME(dennis.oh) Improve performance
        list_to_return = []
        for name1 in source1:

            logger.info(f'Searching for {name1}')
            flag_found = False
            for item0 in source0:
                if item0.user_identifier == user_identifier and item0.name == name1:
                    flag_found = True
                    break

            if not flag_found:
                logger.info(f'Not found: {name1}')
                new_expense_category = ExpenseCategory()
                new_expense_category.user_identifier = user_identifier
                new_expense_category.uuid = self._get_random_pseudo_uuid_for_expense_category(existing_uuid_set)
                new_expense_category.name = name1
                list_to_return.append(new_expense_category)
        return list_to_return

    def _get_existing_uuid_set(self, user_identifier: str) -> set[str]:
        set_to_return = set()
        list_of_category = self.db_impl.get_all_filtered_by_user_identifier(user_identifier)
        for item in list_of_category:
            set_to_return.add(item.uuid)
        return set_to_return

    def _get_random_pseudo_uuid_for_expense_category(self, existing_uuid_set: set[str]):
        const_length_of_pseudo_uuid = 4
        while True:
            uuid = ''
            for _ in range(0, const_length_of_pseudo_uuid):
                # 26 characters. 0-indexed.
                num = ord('a') + random.randint(0, 26 - 1)
                uuid += chr(num)
            if uuid not in existing_uuid_set:
                break
        return uuid

    def _build_category_config(self, category_config_file_path: str) -> dict:
        category_config_to_return = {}
        try:
            config_file = open(category_config_file_path, 'rb')
            category_config_to_return = yaml.safe_load(config_file)
            config_file.close()
        except IOError as e:
            logger.error(f'IOError: {e}')
            logger.error('A configuration file path was: %s' % category_config_file_path)
            return None
        return category_config_to_return
