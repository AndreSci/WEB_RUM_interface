from misc.logger import Logger
from database.db_connection import connect_db


class CardHolder:

    @staticmethod
    def test_user(login_user, inn_dept, logger: Logger) -> dict:
        """ Проверяем логин лк и инн на активность и совпадение """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute("select ID_User, LastName_User, FirstName_User, Desc_User, Active_User, Name_Dept "
                            "from sac3.user, sac3.dept "
                            f"where Login_User = {login_user} "
                            "and Active_User = 1 "
                            "and ID_Dept_user = ID_Dept "
                            f"and INN_Dept = {inn_dept}")
                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'
                    ret_value['data'] = result

                    logger.add_log(f"EVENT\tCardHolder.test_user\tДанные из запроса в БД: {result}", print_it=False)
                else:
                    ret_value['desc'] = "Не удалось найти данные в БД"

            connection.commit()

        except Exception as ex:
            logger.add_log(f"ERROR\tCardHolder.test_user\tОшибка связи с базой данных: {ex}")

        return ret_value

    @staticmethod
    def request_create(card: dict, photo_address: str, logger: Logger) -> dict:
        """ Создает заявку на выдачу постоянных пропусков """

        # FStatusID = 1 (Успешно создан, ожидает решение оператора)

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        last_name = card.get('FLastName')
        first_name = card.get('FFirstName')

        middle_name = card.get('FMiddleName')
        if not middle_name:
            middle_name = ''

        car_number = card.get('FCarNumber')
        if not car_number:
            car_number = ''

        phone = card.get('FPhone')
        if not phone:
            phone = ''

        email = card.get('FEmail')
        if not email:
            email = ''

        desc = ''

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"select * from paidparking.tcompany where FINN = {card.get('inn')}")
                result = cur.fetchall()

                if len(result) > 0:
                    t_company = result[0].get('FID')

                    cur.execute(f"insert into mifarecards.trequestoncreatecardholder "
                                f"(FlastName, FFirstName, FMiddleName, FCarNumber, "
                                f"FPhone, FEmail, FDescription, FTime, FCompanyID, FStatusID, FPhoto) values "
                                f"('{last_name}', '{first_name}', '{middle_name}', '{car_number}', "
                                f"'{phone}', '{email}', '{desc}', now(), {t_company}, 1, '{photo_address}')")

                    ret_value['status'] = "SUCCESS"
                else:
                    ret_value['desc'] = "Не удалось найти компанию по ИНН"

            connection.commit()

        except Exception as ex:
            logger.add_log(f"ERROR\tCardHolder.request_create\tОшибка связи с базой данных: {ex} "
                           f"(данные для заполнения: "
                           f"{last_name} - {first_name} - {middle_name} - {car_number} - {phone} - {email})")
            ret_value['desc'] = "Ошибка на сервере при создании заявки"

        return ret_value

    @staticmethod
    def request_list(inn_company: str, logger: Logger) -> dict:
        """ Запрашивает список заявок на выдачу постоянных пропусков """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"select * from paidparking.tcompany where FINN = {inn_company}")
                result = cur.fetchall()

                if len(result) > 0:
                    t_company = result[0].get('FID')
                    connection.commit()

                    cur.execute(f"select mifarecards.trequestoncreatecardholder.FID, FlastName, FFirstName, "
                                f"FMiddleName, FName as Status "
                                f"from mifarecards.trequestoncreatecardholder, "
                                f"mifarecards.trequestoncreatecardholderstate as State "
                                f"where FCompanyID = {t_company} and State.FID = FStatusID and FActivity = 1")

                    result = cur.fetchall()

                    if len(result) > 0:
                        ret_value['data'] = result
                        ret_value['status'] = "SUCCESS"
                    else:
                        ret_value['desc'] = "Не удалось найти заявки"
                else:
                    ret_value['desc'] = "Не удалось найти компанию по ИНН"

        except Exception as ex:
            logger.add_log(f"ERROR\tCardHolder.request_list\tОшибка связи с базой данных: {ex} "
                           f"(данные для получения: INN {inn_company})")
            ret_value['desc'] = "Ошибка на сервере при запросе списка заявок"

        return ret_value

    @staticmethod
    def cancel_request(login_id: str, inn: str, fid: str, logger: Logger) -> dict:
        """ Меняет статус заявки на Отменён пользователем """

        # FStatusID = 7 (Отменён из личного кабинета)

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"select * from paidparking.tcompany where FINN = {inn}")
                result = cur.fetchall()

                if len(result) > 0:
                    t_company = result[0].get('FID')

                    cur.execute(f"update mifarecards.trequestoncreatecardholder "
                                f"set FActivity = 0, FStatusID = 7 "
                                f"where FID = {fid} "
                                f"and FActivity = 1 "
                                f"and FStatusID = 1 "
                                f"and FCompanyID = {t_company}")

                    result = cur.rowcount

                    if result == 1:
                        ret_value['status'] = "SUCCESS"
                    elif result > 1:
                        ret_value['status'] = "WARNING"
                        logger.add_log(f"ERROR\tCardHolder.cancel_request\tОшибка! Обновлено больше одного запроса "
                                       f"на постоянный пропуск: "
                                       f"fid {fid} user_id {login_id} inn {inn} company_id {t_company}")
                        ret_value['desc'] = "Было отменено несколько заявок"
                    else:
                        logger.add_log(f"WARNING\tCardHolder.cancel_request\tНе удалось найти заявку: "
                                       f"fid {fid} user_id {login_id} inn {inn} company_id {t_company}")
                        ret_value['desc'] = "Не удалось отменить заявку на пропуск, проверьте статус"
                else:
                    ret_value['desc'] = "Не удалось найти компанию по ИНН"

            connection.commit()

        except Exception as ex:
            logger.add_log(f"ERROR\tCardHolder.cancel_request\tОшибка связи с базой данных: {ex} "
                           f"(данные для заполнения: login_id {login_id} inn {inn} fid {fid})")
            ret_value['desc'] = "Ошибка на сервере при создании заявки"

        return ret_value
