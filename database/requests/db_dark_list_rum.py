from misc.logger import Logger
from database.db_connection import connect_db


class DarkListClass:
    """ Класс отвечает за проверку номера авто в черном списке """

    @staticmethod
    def find(car_number, logger: Logger):
        """ Поиск номера в БД Румянцево таблица darklist """

        ret_value = {'RESULT': 'ERROR', 'DESC': '', 'DATA': ''}

        # # -----------------------------
        # # TODO убрать в релизе
        # ret_value['RESULT'] = 'SUCCESS'
        # return ret_value
        # # -----------------------------

        try:
            # Создаем подключение к БД Румянцево
            connection = connect_db(logger, "DATABASE_RUM")

            with connection.cursor() as cur:

                # Загружаем данные из базы
                cur.execute(f"select * from rumyancevo.darklist where AutoNum like '%{car_number}%' and IsActive = 1")

                row_count = cur.rowcount
                res_info = cur.fetchall()

                if row_count == 0:
                    ret_value['RESULT'] = 'SUCCESS'
                else:
                    ret_value['RESULT'] = 'WARNING'
                    ret_value['DESC'] = f"Авто {car_number} находится в черном списке"
                    logger.add_log(f"WARNING\tDarkListClass.find\tНайден номер в черном списке: {res_info}")

            connection.close()

        except Exception as ex:
            logger.add_log(f"EXCEPTION\tDarkListClass.find\tИсключение вызвало: {ex}")
            ret_value['DESC'] = "Ошибка на сервере"

        return ret_value
