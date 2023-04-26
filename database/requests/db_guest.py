from misc.logger import Logger
from database.db_connection import connect_db


class GuestClass:
    """ Класс отвечает за создание/блокировку/проверку пропуска """

    @staticmethod
    def request_pass(json_data: dict, logger: Logger):
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
                                f"{id_remote} )")

                    connection.commit()

                    result = cur.rowcount

                    if result == 1:
                        ret_value['RESULT'] = 'SUCCESS'
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
    def show_status(id_user, logger: Logger):
        """ Получить список заявок для гостей на компанию """

        ret_value = {'RESULT': 'ERROR', 'DESC': '', 'DATA': list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:

                # # Загружаем данные в базу
                # cur.execute(f"select Date_Request, "
                #                 f"DateFrom_Request, DateTo_Request, "
                #                 "Name_LastName, Name_FirstName, Name_MIddleName, Number_Car, "
                #                 "sac3.requeststatus.FName  as FStatus "
                #                 "from sac3.request, sac3.lastname, sac3.firstname, sac3.middlename, "
                #                 "sac3.car, sac3.requeststatus "
                #                 f"where ID_User_Request = {id_user} "
                #                 "and sac3.lastname.ID_LastName = ID_LastName_Request "
                #                 "and ID_FirstName = ID_FirstName_Request "
                #                 "and ID_MiddleName = ID_MiddleName_Request "
                #                 "and ID_Car = ID_Car_Request "
                #                 "and Activity_Request = 1 "
                #                 "and sac3.requeststatus.FID = ID_RequestStatus_Request "
                #                 "and now() between DateFrom_Request and DateTo_Request "
                #                 "order by Date_Request desc")
                # Загружаем данные в базу
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
                        result[index]['FStatus'] = 'Ожидает реализацию в БД'  # TODO убрать когда появиться поле в БД

                    ret_value['DATA'] = result
                else:
                    ret_value['DESC'] = 'Не удалось найти заявки'

            connection.close()

        except Exception as ex:
            logger.add_log(f"EXCEPTION\tGuestClass.request_pass\tИсключение вызвало: {ex}")
            ret_value['DESC'] = "Ошибка на сервере"

        return ret_value

    @staticmethod
    def block_pass(id_remote, logger: Logger):
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
