import pprint
import random

import mariadb
import yaml
from loguru import logger

from tt.db_connection import DBConnection
from tt.db_impl_base import DBImplBase


class ExpenseCategory:

    def __init__(self):
        self.user_identifier = None
        self.uuid = None
        self.name = None

    def __eq__(self, other):
        if isinstance(other, ExpenseCategory):
            return (
                self.user_identifier == other.user_identifier
                and self.uuid == other.uuid
                and self.name == other.name
            )
        return False

    def __hash__(self):
        return hash((self.user_identifier, self.uuid, self.name))

    def __str__(self):
        return f"user_identifier({self.user_identifier}) uuid({self.uuid}) name({self.name})"


class ExpenseCategoryTextPrinterImpl:

    def __init__(self):
        pass

    def print_all(self, list_of_expense_category: list[ExpenseCategory]):
        for e in list_of_expense_category:
            print(pprint.pformat(str(e)))


class ExpenseCategoryDBImpl(DBImplBase):

    def __init__(self, db_connection: DBConnection):
        super().__init__(db_connection)
        self.table_name = "expense_categories"

    def get_all(self) -> list[ExpenseCategory]:
        list_of_expense_category = []
        cur = self.db_connection.cur()
        sql_string = f"SELECT user_identifier, uuid, name FROM {self.table_name};"
        logger.info(sql_string)
        cur.execute(sql_string)
        for user_identifier, uuid, name in cur:
            e = ExpenseCategory()
            e.user_identifier = user_identifier
            e.uuid = uuid
            e.name = name
            list_of_expense_category.append(e)
        return list_of_expense_category

    def create_table(self) -> bool:
        cur = self.db_connection.cur()
        sql_string = (
            f"CREATE TABLE IF NOT EXISTS {self.table_name}(\n"
            "user_identifier varchar(128) not null,\n"
            "uuid varchar(128) not null,\n"
            "name varchar(128) not null\n"
            ")\n"
        )
        sql_string += f"CHARACTER SET '{self.const_default_table_charset}';"
        logger.info(sql_string)
        try:
            cur.execute(sql_string)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)
            return False
        return True

    def get_all_filtered_by_user_identifier(
        self, user_identifier: str
    ) -> list[ExpenseCategory]:
        cur = self.db_connection.cur()
        escaped_user_identifier = self.escape_sql_string(user_identifier)
        sql_string = f"SELECT user_identifier, uuid, name FROM {self.table_name} WHERE user_identifier={escaped_user_identifier}"
        logger.info(sql_string)
        list_of_expense_category = []
        try:
            cur.execute(sql_string)
            for user_identifier, uuid, name in cur:
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
            sql_string = f"INSERT INTO {self.table_name} (user_identifier, uuid, name) VALUES({escaped_user_identifier}, {escaped_uuid}, {escaped_name})"
            logger.info(sql_string)
            try:
                cur.execute(sql_string)
            except mariadb.Error as e:
                self.handle_general_sql_execution_error(e, sql_string)
                return False
        return True

    def drop_table(self) -> bool:
        cur = self.db_connection.cur()
        sql_string = f"DROP TABLE {self.table_name};"
        logger.info(sql_string)
        try:
            cur.execute(sql_string)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)
            return False
        return True


class ExpenseCategoryControl:

    def __init__(self, db_connection: DBConnection):
        self.db_impl = ExpenseCategoryDBImpl(db_connection)

    def import_and_append_from_file(self, category_config_file_path: str) -> bool:
        if not self.db_impl.create_table():
            return False

        category_config = self._build_category_config(category_config_file_path)
        for item in category_config:
            user_identifier = item["user_identifier"]
            existing_list_of_category = (
                self.db_impl.get_all_filtered_by_user_identifier(user_identifier)
            )
            list_of_records_to_insert = self._get_list_of_records_to_insert(
                user_identifier, existing_list_of_category, item["categories"]
            )
            if len(list_of_records_to_insert) > 0:
                self.db_impl.insert_records(list_of_records_to_insert)
        return True

    def get_all_filtered_by_user_identifier(
        self, user_identifier: str
    ) -> list[ExpenseCategory]:
        list_of_expense_category = self.db_impl.get_all_filtered_by_user_identifier(
            user_identifier
        )
        return list_of_expense_category

    def get_all(self) -> list[ExpenseCategory]:
        list_of_expense_category = self.db_impl.get_all()
        return list_of_expense_category

    def delete(self) -> bool:
        return self.db_impl.drop_table()

    def _get_list_of_records_to_insert(
        self, user_identifier: str, source0: list[ExpenseCategory], source1: list[str]
    ) -> list[str]:
        # Get the diff.
        set_of_names_from_source0 = set()
        for item in source0:
            set_of_names_from_source0.add(item.name)
        set_of_names_from_source1 = set()
        for name in source1:
            set_of_names_from_source1.add(name)
        logger.info(f"set_of_source0. length({len(set_of_names_from_source0)})")
        logger.info(f"set_of_source1. length({len(set_of_names_from_source1)})")
        set_of_diff = set_of_names_from_source1 - set_of_names_from_source0
        list_of_diff = list(set_of_diff)

        # Build a list to return.
        list_to_return = []
        existing_uuid_set = self._get_existing_uuid_set(user_identifier)
        for name in list_of_diff:
            logger.info(f"Adding {name}...")
            new_expense_category = ExpenseCategory()
            new_expense_category.user_identifier = user_identifier
            new_expense_category.uuid = (
                self._get_random_pseudo_uuid_for_expense_category(existing_uuid_set)
            )
            new_expense_category.name = name
            list_to_return.append(new_expense_category)
        logger.info(f"The length of list_to_return is {len(list_to_return)}")
        return list_to_return

    def _get_existing_uuid_set(self, user_identifier: str) -> set[str]:
        set_to_return = set()
        list_of_category = self.db_impl.get_all_filtered_by_user_identifier(
            user_identifier
        )
        for item in list_of_category:
            set_to_return.add(item.uuid)
        return set_to_return

    def _get_random_pseudo_uuid_for_expense_category(self, existing_uuid_set: set[str]):
        const_length_of_pseudo_uuid = 4
        while True:
            uuid = ""
            for _ in range(0, const_length_of_pseudo_uuid):
                # 26 characters. 0-indexed.
                num = ord("a") + random.randint(0, 26 - 1)
                uuid += chr(num)
            if uuid not in existing_uuid_set:
                break
        return uuid

    def _build_category_config(self, category_config_file_path: str) -> dict:
        category_config_to_return = {}
        try:
            config_file = open(category_config_file_path, "rb")
            category_config_to_return = yaml.safe_load(config_file)
            config_file.close()
        except IOError as e:
            logger.error(f"IOError: {e}")
            logger.error(
                "A configuration file path was: %s" % category_config_file_path
            )
            return None
        return category_config_to_return
