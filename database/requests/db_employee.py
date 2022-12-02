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
            logger.add_log(f"ERROR\tEmployeeDB.add_phone\tОшибка связи с базой данных: {ex}")

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

    @staticmethod
    def set_car_number(guid: str, car_number: str, logger: Logger) -> dict:
        """ принимает FGUID сотрудника и номер авто"""

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"select FID from paidparking.temployee where FGUID = '{guid}'")

                result = cur.fetchall()

                if len(result) > 0:
                    fid = result[0]['FID']
                    cur.execute(f"insert into paidparking.tcaremployee (FPlate, FEmployeeID) "
                                f"values ('{car_number}', {fid})")

                    connection.commit()

                    ret_value['status'] = 'SUCCESS'
                else:
                    ret_value['desc'] = f"Не удалось найти сотрудника: {guid}"
                    logger.add_log(f"ERROR\tEmployeeDB.take\tНе удалось найти сотрудника: {guid}")

        except Exception as ex:
            logger.add_log(f"ERROR\tEmployeeDB.set_car_number\tОшибка связи с базой данных: {ex}")

        return ret_value

    @staticmethod
    def get_car_numbers(guid: str, logger: Logger) -> dict:
        """ принимает FGUID сотрудника """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"select FPlate from paidparking.temployee, paidparking.tcaremployee "
                            f"where temployee.FGUID = '{guid}' "
                            f"and tcaremployee.FEmployeeID = temployee.FID")

                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'
                    ret_value['data'] = result
                else:
                    ret_value['desc'] = "Не удалось найти данные в БД"

        except Exception as ex:
            logger.add_log(f"ERROR\tEmployeeDB.get_car_number\tОшибка связи с базой данных: {ex}")

        return ret_value

    @staticmethod
    def remove_car_number(guid: str, car_number: str, logger: Logger) -> dict:
        """ принимает FGUID сотрудника """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"select tcaremployee.FID from paidparking.temployee, paidparking.tcaremployee "
                            f"where temployee.FGUID = '{guid}' "
                            f"and tcaremployee.FEmployeeID = temployee.FID and FPlate = '{car_number}'")

                result = cur.fetchall()

                if len(result) > 0:
                    fid_number = result[0]['FID']

                    cur.execute(f"delete from paidparking.tcaremployee where FID = {fid_number}")

                    ret_value['status'] = 'SUCCESS'

                else:
                    ret_value['desc'] = "Не удалось найти данные в БД"

                connection.commit()

        except Exception as ex:
            logger.add_log(f"ERROR\tEmployeeDB.get_car_number\tОшибка связи с базой данных: {ex}")
            ret_value['desc'] = ex

        return ret_value

    @staticmethod
    def set_auto_balance(guid: int, units: int, logger: Logger) -> dict:
        """ принимает FGUID сотрудника, phone_number и отвечает словарем dict() """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        if units == 0:
            units = 'null'

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"update paidparking.temployee set FAutobalance = {units} where FGUID = '{guid}'")

                connection.commit()

                ret_value['status'] = 'SUCCESS'

        except Exception as ex:
            logger.add_log(f"ERROR\tEmployeeDB.add_phone\tОшибка связи с базой данных: {ex}")

        return ret_value
