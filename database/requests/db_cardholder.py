from misc.logger import Logger
from database.db_connection import connect_db


class CardHolder:
    @staticmethod
    def request_create(card: dict, logger: Logger) -> dict:
        """ принимает GUID введенный пользователем и отвечает словарем dict() \n
         duration должен содержать два поля 'data_from' и 'data_to' """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute("select * from mifarecards.trequestoncreatecardholder")
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
