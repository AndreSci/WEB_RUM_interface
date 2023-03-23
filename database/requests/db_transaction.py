from misc.logger import Logger
from database.db_connection import connect_db


class TransactionDB:
    @staticmethod
    def take_employee(guid: int, duration: dict, logger: Logger) -> dict:
        """ принимает GUID введенный пользователем и отвечает словарем dict() \n
         duration должен содержать два поля 'data_from' и 'data_to' """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute("select FValue, FName as FTransactionType, "
                            "DATE_FORMAT(FTime, '%Y-%m-%d %H:%i:%s') as FTime "
                            "from paidparking.ttransaction, paidparking.temployee, paidparking.ttypetransaction "
                            "where (fguid = fguidto or fguid = FGUIDFrom) "
                            "and FTTypeTransactionid = ttypetransaction.FID "
                            f"and temployee.FGUID = '{guid}' "
                            f"and FTime between '{duration['data_from']}' and '{duration['data_to']}' "
                            "order by FTime")
                result = cur.fetchall()

                print(result)

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'
                    ret_value['data'] = result
                else:
                    ret_value['desc'] = "Не удалось найти данные в БД"

            connection.commit()

        except Exception as ex:
            logger.add_log(f"ERROR\tTransactionDB.take\tОшибка связи с базой данных: {ex}")

        return ret_value

    @staticmethod
    def take_company(guid: str, duration: dict, logger: Logger) -> dict:
        """ принимает FGUID введенный пользователем и отвечает словарем dict() \n
         duration должен содержать два поля 'data_from' и 'data_to' """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute("SELECT ttransaction.FValue, "
                            "ttypetransaction.FName as FTransactionTypeName, "
                            "ttransaction.FGUIDFrom, ttransaction.FGUIDTo, "
                            f"DATE_FORMAT(ttransaction.FTime, '%Y-%m-%d %H:%i:%s') as FTime "
                            "FROM paidparking.ttransaction, paidparking.ttypetransaction "
                            f"where (ttransaction.FGUIDFrom = '{guid}' "
                            f"or ttransaction.FGUIDTo = '{guid}') "
                            "and ttransaction.FTTypeTransactionID = ttypetransaction.FID "
                            f"and FTime between '{duration['data_from']}' and '{duration['data_to']}' "
                            "order by FTime")
                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'
                    ret_value['data'] = result
                else:
                    ret_value['desc'] = "Не удалось найти данные в БД"

            connection.commit()

        except Exception as ex:
            logger.add_log(f"ERROR\tTransactionDB.take_company\tОшибка связи с базой данных: {ex}")

        return ret_value

