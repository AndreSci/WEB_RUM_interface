from misc.logger import Logger
from database.db_connection import connect_db


class EmployeeDB:
    @staticmethod
    def set_favorite(guid: str, is_favorite: int, logger: Logger) -> dict:
        """ принимает FGUID сотрудника и 1 или 0 """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"update paidparking.temployee set FFavorite = {is_favorite} where FGUID = '{guid}'")

                connection.commit()

                ret_value['status'] = 'SUCCESS'

        except Exception as ex:
            logger.add_log(f"ERROR\tEmployeeDB.take\tОшибка связи с базой данных: {ex}")

        return ret_value

    @staticmethod
    def add_phone(guid: int, phone_number: str, logger: Logger) -> dict:
        """ принимает FGUID сотрудника, phone_number и отвечает словарем dict() """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"update paidparking.temployee set FPhone = '{phone_number}' where FGUID = '{guid}'")

                connection.commit()

                ret_value['status'] = 'SUCCESS'

        except Exception as ex:
            logger.add_log(f"ERROR\tEmployeeDB.take\tОшибка связи с базой данных: {ex}")

        return ret_value

    @staticmethod
    def add_email(guid: int, email: str, logger: Logger) -> dict:
        """ принимает FGUID сотрудника, email и отвечает словарем dict() """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"update paidparking.temployee set FEmail = '{email}' where FGUID = '{guid}'")

                connection.commit()

                ret_value['status'] = 'SUCCESS'

        except Exception as ex:
            logger.add_log(f"ERROR\tEmployeeDB.take\tОшибка связи с базой данных: {ex}")

        return ret_value

    @staticmethod
    def add_phone_email(guid: int, phone_number: str, email: str, logger: Logger) -> dict:
        """ принимает FGUID сотрудника, email, phone_number и отвечает словарем dict() """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"update paidparking.temployee set FPhone = '{phone_number}', FEmail = '{email}' "
                            f"where FGUID = '{guid}'")

                connection.commit()

                ret_value['status'] = 'SUCCESS'

        except Exception as ex:
            logger.add_log(f"ERROR\tEmployeeDB.take\tОшибка связи с базой данных: {ex}")

        return ret_value
