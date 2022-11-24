from misc.logger import Logger
from database.db_connection import connect_db


class DecreaseDB:
    @staticmethod
    def take(fid: int, duration: dict, logger: Logger) -> dict:
        """ принимает FID введенный пользователем и отвечает словарем dict() \n
         duration должен содержать два поля 'start' и 'end' """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                # Ищем статистику
                cur.execute(f"select FDecreaseDate, FName, FValue "
                            f"from paidparking.tdecreases, paidparking.ttypedecrease "
                            f"where FTypeDecreaseID = ttypedecrease.FID "
                            f"and FEmployeeID = {fid} "
                            f"and FDecreaseDate between '{duration['start']}' and '{duration['end']}' "
                            f"order by FDecreaseDate")
                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'
                    ret_value['data'] = result

        except Exception as ex:
            logger.add_log(f"ERROR\tDecreaseDB.take\tОшибка связи с базой данных: {ex}")

        return ret_value
