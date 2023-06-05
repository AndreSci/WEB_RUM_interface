from misc.logger import Logger
from database.db_connection import connect_db_rum


class DarkListClass:
    """ Класс отвечает за проверку номера авто в черном списке """

    @staticmethod
    def find(car_number, logger: Logger):
        """ Поиск номера в БД Румянцево таблица darklist """

        ret_value = {'RESULT': 'ERROR', 'DESC': '', 'DATA': ''}

        # TODO убрать в релизе
        ret_value['RESULT'] = 'SUCCESS'
        return ret_value

        try:
            # Создаем подключение
            connection = connect_db_rum(logger)

            with connection.cursor() as cur:

                # Загружаем данные из базы
                # TODO получить уточняющую информацию по запросам от Вовы
                cur.execute(f"select * from sac3.darklist where car_number = '{car_number}'")

                result = cur.rowcount

                if result == 0:
                    ret_value['RESULT'] = 'SUCCESS'
                else:
                    ret_value['RESULT'] = 'WARNING'
                    ret_value['DESC'] = f"Авто {car_number} заблокировано"

            connection.close()

        except Exception as ex:
            logger.add_log(f"EXCEPTION\tDarkListClass.find\tИсключение вызвало: {ex}")
            ret_value['DESC'] = "Ошибка на сервере"

        return ret_value
