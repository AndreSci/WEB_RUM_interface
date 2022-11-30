from misc.logger import Logger
from database.db_connection import connect_db


class DecreaseDB:
    @staticmethod
    def take(guid: int, duration: dict, logger: Logger) -> dict:
        """ принимает GUID сотрудника и отвечает словарем dict() \n
         duration должен содержать два поля 'data_from' и 'data_to' """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                # Ищем статистику
                cur.execute(f"select FDecreaseDate, FName, FValue "
                            f"from paidparking.tdecreases, paidparking.ttypedecrease, paidparking.temployee "
                            f"where FTypeDecreaseID = ttypedecrease.FID "
                            f"and temployee.FGUID = '{guid}' "
                            f"and FEmployeeID = temployee.FID "
                            f"and FDecreaseDate between '{duration['data_from']}' and '{duration['data_to']}' "
                            f"order by FDecreaseDate")
                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'
                    ret_value['data'] = result

        except Exception as ex:
            logger.add_log(f"ERROR\tDecreaseDB.take\tОшибка связи с базой данных: {ex}")

        return ret_value
