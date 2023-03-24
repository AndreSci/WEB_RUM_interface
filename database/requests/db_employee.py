from misc.logger import Logger
from database.db_connection import connect_db
from misc.take_uid import UserUid


class EmployeeDB:

    @staticmethod
    def take_employee_info(req_text: str, logger: Logger) -> dict:
        """ Принимает подготовленный текст для условия запроса SQL """

        ret_value = {"RESULT": "ERROR", "DESC": '', "DATA": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"select FID, FApacsID, FActivity, FBlocked, FCompanyAccount, FPersonalAccount, "
                            f"FEmail, FPhone, FFavorite, "
                            f"FLastName, FFirstName, FMiddleName, "
                            f"FLastDecreaseDate, FCreateDate, FLastModifyDate, FGUID "
                            f"from paidparking.temployee "
                            f"where {req_text}")

                result = cur.fetchall()

                if cur.rowcount > 0:
                    result[0]['UID'] = UserUid.take(result[0].get('FApacsID'), result[0].get('FID'))
                    result[0]['FCreateDate'] = str(result[0]['FCreateDate'])
                    result[0]['FLastDecreaseDate'] = str(result[0]['FLastDecreaseDate'])
                    result[0]['FLastModifyDate'] = str(result[0]['FLastModifyDate'])

                    try:
                        del result[0]['FID']
                        del result[0]['FApacsID']
                    except Exception as ex:
                        logger.add_log(f"ERROR\tEmployeeDB.take_employee_info\t"
                                       f"Не удалось удалить данные из словаря: {ex}")

                    ret_value['DATA'] = result
                    ret_value['RESULT'] = 'SUCCESS'
                else:
                    ret_value['DESC'] = "Не удалось найти сотрудника по данному GUID"

        except Exception as ex:
            logger.add_log(f"ERROR\tEmployeeDB.take_employee_info\tОшибка связи с базой данных: {ex}")
            ret_value['DESC'] = "Ошибка на сервере"

        return ret_value

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
                    cur.execute(f"insert into paidparking.tplateemployee (FPlate, FEmployeeID) "
                                f"values ('{car_number}', {fid})")

                    connection.commit()

                    ret_value['status'] = 'SUCCESS'
                else:
                    ret_value['desc'] = f"Не удалось найти сотрудника: {guid}"
                    logger.add_log(f"ERROR\tEmployeeDB.take\tНе удалось найти сотрудника: {guid}")

        except Exception as ex:
            logger.add_log(f"ERROR\tEmployeeDB.set_car_number\tОшибка связи с базой данных: {ex}")

            if 'Duplicate' in str(ex):
                ret_value['desc'] = "Данный номер автомобиля уже занят другим сотрудником"
            else:
                ret_value['desc'] = "Ошибка на сервере"

        return ret_value

    @staticmethod
    def get_car_numbers(guid: str, logger: Logger) -> dict:
        """ принимает FGUID сотрудника """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"select FPlate, tplateemployee.FID as FPlateID "
                            f"from paidparking.temployee, paidparking.tplateemployee "
                            f"where temployee.FGUID = '{guid}' "
                            f"and tplateemployee.FEmployeeID = temployee.FID")

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
    def remove_car_number(guid: str, f_plate_id: str, logger: Logger) -> dict:
        """ принимает FGUID сотрудника """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"select FID from paidparking.temployee "
                            f"where temployee.FGUID = '{guid}' ")

                result = cur.fetchall()

                if len(result) > 0:
                    fid_employee = result[0]['FID']

                    cur.execute(f"delete from paidparking.tplateemployee "
                                f"where FID = {f_plate_id} "
                                f"and FEmployeeID = {fid_employee}")

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
