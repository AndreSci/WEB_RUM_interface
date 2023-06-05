from misc.logger import Logger
from database.db_connection import connect_db


class GuestClass:
    """ Класс отвечает за создание/блокировку/проверку пропуска """

    @staticmethod
    def request_pass(json_data: dict, id_request_status: int, logger: Logger) -> dict:
        """ Принимает словарь с данными, так же IDRemote(id получаемый в ЛК отдельно) и ID_User(id ЛК) """

        ret_value = {'RESULT': 'ERROR', 'DESC': '', 'DATA': list()}

        login_user = json_data['user_id']
        id_remote = json_data['id_remote']

        last_name = json_data['FLastName']
        first_name = json_data['FFirstName']

        middle_name = json_data.get('FMiddleName')

        if not middle_name:
            middle_name = ''

        car_number = json_data.get('FCarNumber')

        if not car_number:
            car_number = ''

        date_from = json_data['FDateFrom']
        date_to = json_data['FDateTo']
        id_ip = '0.0.0.0'

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                # Ищем фамилию
                cur.execute(f"select * from sac3.lastname where Name_LastName = '{last_name}'")
                request_last_name = cur.fetchall()
                if len(request_last_name) == 0:
                    cur.execute(f"insert into sac3.lastname(Name_LastName) values ('{last_name}')")
                    connection.commit()
                    cur.execute(f"select * from sac3.lastname where Name_LastName = '{last_name}'")
                    request_last_name = cur.fetchall()

                # Ищем имя
                cur.execute(f"select * from sac3.firstname where Name_FirstName = '{first_name}'")
                request_first_name = cur.fetchall()
                if len(request_first_name) == 0:
                    cur.execute(f"insert into sac3.firstname(Name_FirstName) values ('{first_name}')")
                    connection.commit()
                    cur.execute(f"select * from sac3.firstname where Name_FirstName = '{first_name}'")
                    request_first_name = cur.fetchall()

                # Ищем отчество
                if middle_name:
                    cur.execute(f"select * from sac3.middlename where Name_MIddleName = '{middle_name}'")
                    request_middle_name = cur.fetchall()
                    if len(request_middle_name) == 0:
                        cur.execute(f"insert into sac3.middlename(Name_MIddleName) values ('{middle_name}')")
                        connection.commit()
                        cur.execute(f"select * from sac3.middlename where Name_MIddleName = '{middle_name}'")
                        request_middle_name = cur.fetchall()

                # Ищем номер машины
                if car_number:
                    cur.execute(f"select * from sac3.car where Number_Car = '{car_number}'")
                    request_car_number = cur.fetchall()
                    if len(request_car_number) == 0:
                        cur.execute(f"insert into sac3.car(Number_Car) values ('{car_number}')")
                        connection.commit()
                        cur.execute(f"select * from sac3.car where Number_Car = '{car_number}'")
                        request_car_number = cur.fetchall()

                # Ищем ip
                cur.execute(f"select * from sac3.ip where Value_IP = '{id_ip}'")
                request_id_ip = cur.fetchall()
                if len(request_id_ip) == 0:
                    cur.execute(f"insert into sac3.ip(Value_IP) values ('{id_ip}')")
                    connection.commit()
                    cur.execute(f"select * from sac3.ip where Value_IP = '{id_ip}'")
                    request_id_ip = cur.fetchall()

                # Ищем id_user
                cur.execute(f"select * from sac3.user where Login_User = {login_user} and Active_User = 1")
                take_user = cur.fetchall()

                if len(take_user) == 1:
                    id_user = take_user[0]['ID_User']

                    # Загружаем данные в базу
                    cur.execute(f"insert into sac3.request("
                                f"ID_User_Request, "
                                f"ID_LastName_Request, "
                                f"ID_FirstName_Request, "
                                f"ID_MiddleName_Request, "
                                f"ID_Car_Request, "
                                f"Date_Request, "
                                f"ID_IP_Request, "
                                f"DateFrom_Request, "
                                f"DateTo_Request, "
                                f"IDRemote_Request) "
                                f"values ("
                                f"{id_user}, "
                                f"{request_last_name[0]['ID_LastName']}, "
                                f"{request_first_name[0]['ID_FirstName']}, "
                                f"{request_middle_name[0]['ID_MiddleName']}, "
                                f"{request_car_number[0]['ID_Car']}, "
                                f"now(), "
                                f"{request_id_ip[0]['ID_IP']}, "
                                f"'{date_from}', "
                                f"'{date_to}', "
                                f"{id_remote})")

                    connection.commit()

                    id_request = cur.lastrowid
                    result = cur.rowcount

                    cur.execute(f"insert into sac3.requeststatus_status(ID_Request, "
                                f"ID_RequestStatus, DateTime) values ({id_request}, {id_request_status}, now())")
                    connection.commit()

                    if result == 1:
                        if id_request_status == 1:
                            ret_value['RESULT'] = 'SUCCESS'
                            ret_value["DESC"] = "Пропуск заказан"
                        else:
                            ret_value['RESULT'] = "WARNING"
                            ret_value["DESC"] = "Пропуск заказан, автомобиль в черном списке."
                    else:
                        ret_value['RESULT'] = 'WARNING'
                        ret_value['DESC'] = 'Проверьте список заявок на пропуска для гостей'
                        logger.add_log(f"WARNING\tGuestClass.request_pass\t"
                                       f"Ответ БД гласит что не было изменений или больше 1: row = {result}")
                else:
                    ret_value['DESC'] = f"Не удалось найти активного пользователя"
                    logger.add_log(f"ERROR\tGuestClass.request_pass\t"
                                   f"Не удалось найти активного пользователя: {login_user}")

            connection.close()

        except Exception as ex:
            logger.add_log(f"EXCEPTION\tGuestClass.request_pass\tИсключение вызвало: {ex}")
            ret_value['DESC'] = "Ошибка на сервере"

        return ret_value

    @staticmethod
    def get_list(id_user, logger: Logger) -> dict:
        """ Получить список заявок для гостей на компанию """

        ret_value = {'RESULT': 'ERROR', 'DESC': '', 'DATA': list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:

                cur.execute(f"select Date_Request, "
                            f"DateFrom_Request, DateTo_Request, "
                            "Name_LastName, Name_FirstName, Name_MIddleName, Number_Car "
                            "from sac3.request, sac3.lastname, sac3.firstname, sac3.middlename, sac3.car "
                            f"where ID_User_Request = {id_user} "
                            "and sac3.lastname.ID_LastName = ID_LastName_Request "
                            "and ID_FirstName = ID_FirstName_Request "
                            "and ID_MiddleName = ID_MiddleName_Request "
                            "and ID_Car = ID_Car_Request "
                            "and Activity_Request = 1 "
                            "and now() between DateFrom_Request and DateTo_Request "
                            "order by Date_Request desc")

                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['RESULT'] = 'SUCCESS'

                    for index in range(len(result)):
                        result[index]['DateFrom_Request'] = str(result[index]['DateFrom_Request'])
                        result[index]['DateTo_Request'] = str(result[index]['DateTo_Request'])
                        result[index]['Date_Request'] = str(result[index]['Date_Request'])

                    ret_value['DATA'] = result
                else:
                    ret_value['DESC'] = 'Не удалось найти заявки'

            connection.close()

        except Exception as ex:
            logger.add_log(f"EXCEPTION\tGuestClass.get_list\tИсключение вызвало: {ex}")
            ret_value['DESC'] = "Ошибка на сервере"

        return ret_value

    @staticmethod
    def get_status(id_request, id_user, logger: Logger) -> dict:
        """ Получить статус заявок для гостей на компанию """

        ret_value = {'RESULT': 'ERROR', 'DESC': '', 'DATA': list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:

                cur.execute(f"select Date_Request, "
                                f"DateFrom_Request, DateTo_Request, "
                                "Name_LastName, Name_FirstName, Name_MIddleName, Number_Car, "
                                "RS.Fname as Status, RSS.DateTime "
                                "from sac3.request, sac3.lastname, sac3.firstname, sac3.middlename, sac3.car, "
                                "sac3.requeststatus_status as RSS, sac3.requeststatus as RS "
                                f"where sac3.request.ID_Request = {id_request} "
                                f"and ID_User_Request = {id_user} "
                                "and sac3.lastname.ID_LastName = ID_LastName_Request "
                                "and ID_FirstName = ID_FirstName_Request "
                                "and ID_MiddleName = ID_MiddleName_Request "
                                "and ID_Car = ID_Car_Request "
                                "and RS.FID = RSS.ID_RequestStatus "
                                "and RSS.ID_Request = sac3.request.ID_Request "
                                "and Activity_Request = 1 "
                                "and now() between DateFrom_Request and DateTo_Request "
                                "order by RSS.DateTime desc")

                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['RESULT'] = 'SUCCESS'

                    result[0]['DateFrom_Request'] = str(result[0]['DateFrom_Request'])
                    result[0]['DateTo_Request'] = str(result[0]['DateTo_Request'])
                    result[0]['Date_Request'] = str(result[0]['Date_Request'])
                    result[0]['DateTime'] = str(result[0]['DateTime'])

                    ret_value['DATA'] = result[0]
                else:
                    ret_value['DESC'] = 'Не удалось найти заявки'

            connection.close()

        except Exception as ex:
            logger.add_log(f"EXCEPTION\tGuestClass.get_status\tИсключение вызвало: {ex}")
            ret_value['DESC'] = "Ошибка на сервере"

        return ret_value

    @staticmethod
    def block_pass(id_remote, logger: Logger) -> dict:
        """ Блокировка пропуска для гостя """

        ret_value = {'RESULT': 'ERROR', 'DESC': '', 'DATA': ''}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:

                # Загружаем данные в базу
                cur.execute(f"update sac3.request set Activity_Request = 0 where IDRemote_Request = {id_remote}")

                connection.commit()

                result = cur.rowcount

                if result == 1:
                    ret_value['RESULT'] = 'SUCCESS'
                    logger.add_log(f"EVENT\tGuestClass.block_pass\tЗаблокирована заявка: {id_remote}")
                elif result == 0:
                    ret_value['RESULT'] = 'WARNING'
                    ret_value['DESC'] = 'Не удалось найти активную заявку'
                    logger.add_log(f"WARNING\tGuestClass.block_pass\tНе удалось найти активную заявку: {id_remote}")
                else:
                    ret_value['RESULT'] = 'WARNING'
                    ret_value['DESC'] = "Было заблокировано больше 1 заявки"
                    logger.add_log(f"WARNING\tGuestClass.block_pass\t"
                                   f"Запрос на блокировку заявки на пропуск гостя привёл к "
                                   f"блокировке нескольких заявок: id_remote {id_remote} - count {result}")

            connection.close()

        except Exception as ex:
            logger.add_log(f"EXCEPTION\tGuestClass.block_pass\tИсключение вызвало: {ex}")
            ret_value['DESC'] = "Ошибка на сервере"

        return ret_value

    @staticmethod
    def change_status(id_request, id_request_status: int, id_user, logger: Logger) -> dict:
        """ Блокировка пропуска для гостя """

        ret_value = {'RESULT': 'ERROR', 'DESC': '', 'DATA': ''}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:

                # Проверяем чтоб номер статуса не выходил за рамки доступных статусов
                cur.execute(f"select * from sac3.requeststatus where FID = {id_request_status}")

                len_status = cur.rowcount

                if len_status == 0:
                    ret_value['DESC'] = f"Не удалось найти тип статуса: {id_request_status}"
                    return ret_value

                # Проверяем принадлежность пользователя к заявке
                cur.execute(f"select ID_Request from sac3.request "
                            f"where ID_Request = {id_request} "
                            f"and ID_User_Request = {id_user}")

                allow_it = cur.fetchone()

                if allow_it:
                    # Загружаем данные в базу
                    cur.execute(f"insert into sac3.requeststatus_status(ID_Request, "
                                f"ID_RequestStatus, DateTime) values ({id_request}, {id_request_status}, now())")
                    connection.commit()

                    result = cur.rowcount
                else:
                    result = 0

                if result == 1:
                    ret_value['RESULT'] = 'SUCCESS'
                    logger.add_log(f"EVENT\tGuestClass.change_status\tИзменен статус гостю: {id_request}")
                elif result == 0:
                    ret_value['RESULT'] = 'WARNING'
                    ret_value['DESC'] = 'Не удалось найти активную заявку'
                    logger.add_log(f"WARNING\tGuestClass.change_status\tНе удалось найти активную заявку: {id_request}")
                else:
                    ret_value['RESULT'] = 'WARNING'
                    ret_value['DESC'] = "Было изменено больше одной заявки"
                    logger.add_log(f"WARNING\tGuestClass.change_status\t"
                                   f"Запрос на изменение статуса заявки на пропуск гостя привёл к "
                                   f"изменению нескольких заявок: id_remote {id_request} - count {result}")

            connection.close()

        except Exception as ex:
            logger.add_log(f"EXCEPTION\tGuestClass.change_status\tИсключение вызвало: {ex}")
            ret_value['DESC'] = "Ошибка на сервере"

        return ret_value
