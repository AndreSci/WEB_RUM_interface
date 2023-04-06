from misc.logger import Logger
from database.db_connection import connect_db


class GuestClass:
    """ Класс отвечает за создание/блокировку/проверку пропуска """

    @staticmethod
    def request_pass(json_data: dict, logger: Logger):
        """ Принимает словарь с данными, так же IDRemote(id получаемый в ЛК отдельно) и ID_User(id ЛК) """

        ret_value = {'RESULT': 'ERROR', 'DESC': '', 'DATA': list()}

        user_id = json_data['user_id']
        id_remote = json_data['id_remote']

        last_name = json_data['FLastName']
        first_name = json_data['FFirstName']
        middle_name = json_data['FMiddleName']
        car_number = json_data['FCarNumber']
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
                cur.execute(f"select * from sac3.middlename where Name_MIddleName = '{middle_name}'")
                request_middle_name = cur.fetchall()
                if len(request_middle_name) == 0:
                    cur.execute(f"insert into sac3.middlename(Name_MIddleName) values ('{middle_name}')")
                    connection.commit()
                    cur.execute(f"select * from sac3.middlename where Name_MIddleName = '{middle_name}'")
                    request_middle_name = cur.fetchall()

                # Ищем номер машины
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
                            f"{user_id}, "
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

            connection.close()

        except Exception as ex:
            logger.add_log(f"EXCEPTION\tGuestClass.request_pass\tИсключение вызвало: {ex}")
            ret_value['DESC'] = "Ошибка на сервере"

        return ret_value

    def show_status(self):
        pass

    def block_pass(self):
        pass
