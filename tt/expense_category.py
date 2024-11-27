# from db_impl_base import DBImplBase
import yaml

from loguru import logger
import mariadb

from db_connection import DBConnection
from db_impl_base import DBImplBase


class ExpenseCategoryIR():

    def __init__(self):
        self.user_identifier = None
        self.uuid = None
        self.name = None


class ExpenseCategoryDBImpl(DBImplBase):

    def __init__(self, db_connection: DBConnection):
        super().__init__(db_connection)

    def get_all(self) -> list[SimpleTransaction]:
        list_of_expense_category_ir = []
        cur = self.db_connection.cur()
        sql_string = 'SELECT uuid, name FROM expense_category;'
        cur.execute(sql_string)
        for (uuid, name) in cur:
            e = ExpenseCategoryIR()
            e.uuid = uuid
            e.name = name
            list_of_expense_category_ir.append(t)
        return list_of_expense_category_ir

    def replace_all(self, list_of_expense_cateogory_ir: list[ExpenseCategoryIR]) -> None:
        pass

    def _create_table(self):
        pass

    def _drop_table(self):
        pass

    def _read_table(self) -> list[ExpenseCategoryIR]:
        pass


class ExpenseCategoryControl():

    def __init__(self):
        self.db_impl = None

    def create_or_update(self, category_config_file_path: str) -> bool:
        category_config = self._build_global_config(category_config_file_path)
        return False

    def _build_global_config(self, category_config_file_path: str) -> dict:
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


def main():
    # @TODO(dennis.oh) Remove main.
    control = ExpenseCategoryControl()
    category_config_file_path = './config/category.yaml'
    control.create_or_update(category_config_file_path)


if __name__ == '__main__':
    main()
