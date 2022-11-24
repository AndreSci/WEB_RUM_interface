from misc.logger import Logger
from database.db_connection import connect_db


class TransactionDB:
    @staticmethod
    def take(fid: int, duration: dict, logger: Logger) -> dict:
        """ принимает FID введенный пользователем и отвечает словарем dict() \n
         duration должен содержать два поля 'start' и 'end' """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:

                cur.execute(f"select FTime, FValue, FName "
                            f"from paidparking.ttransaction, paidparking.temployee, paidparking.ttypetransaction "
                            f"where (fguid = fguidto or fguid = FGUIDFrom) "
                            f"and FTTypeTransactionid = ttypetransaction.FID "
                            f"and temployee.fid = {fid} "
                            f"and FTime between '{duration['start']}' and '{duration['end']}' "
                            f"order by FTime")
                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'
                    ret_value['data'] = result

        except Exception as ex:
            logger.add_log(f"ERROR\tTransactionDB.take\tОшибка связи с базой данных: {ex}")

        return ret_value
