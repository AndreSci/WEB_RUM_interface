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
    def recreate_request(empl_info: dict, logger: Logger) -> dict:
        """ Создаем заявку на выпуск пропуска """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        inn_company = empl_info.get('inn')
        f_apacs_id = empl_info.get('FApacsID')

        last_name = empl_info.get('FLastName')
        first_name = empl_info.get('FFirstName')
        middle_name = empl_info.get('FMiddleName')
        car_number = empl_info.get('FCarNumber')

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"select * from paidparking.tcompany where FINN = {inn_company}")
                result = cur.fetchall()

                if len(result) > 0:
                    t_company = result[0].get('FID')

                    cur.execute(f"insert into mifarecards.trequestoncreatecardholder "
                                f"(FlastName, FFirstName, FMiddleName, "
                                f"FCarNumber, FEmail, FPhoto, FPhone, "
                                f"FDescription, FTime, FCompanyID, FStatusID, FApacsID) "
                                f"values "
                                f"('{last_name}', '{first_name}', '{middle_name}', "
                                f"'{car_number}', '', '', '', "
                                f"'', now(), {t_company}, 1, {f_apacs_id})")

                    connection.commit()

                    result = cur.rowcount

                    if result == 1:
                        ret_value['status'] = "SUCCESS"
                    elif result > 1:
                        ret_value['status'] = "WARNING"
                        logger.add_log(f"ERROR\tCardHolder.recreate_request\tБыло создано более одной заявки: "
                                       f"{empl_info}")
                        ret_value['desc'] = "Было создано более одной заявки"
                    else:
                        logger.add_log(f"ERROR\tCardHolder.recreate_request\tНе удалось создать заявку: {empl_info}")
                        ret_value['desc'] = "Не удалось создать заявку на перевыпуск"

                else:
                    ret_value['desc'] = "Не удалось найти компанию по ИНН"

        except Exception as ex:
            logger.add_log(f"ERROR\tCardHolder.recreate_request\tОшибка связи с базой данных: {ex} "
                           f"(данные для заполнения: {empl_info})")
            ret_value['desc'] = "Ошибка на сервере при создании заявки"

        return ret_value

    @staticmethod
    def block_card_holder(login_id: str, inn: str, f_apacs_id: str, logger: Logger) -> dict:
        """ Блокирует пропуск сотруднику по Apacs ID """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)
            with connection.cursor() as cur:

                cur.execute(f"select * from paidparking.tcompany where FINN = {inn}")
                result = cur.fetchall()

                if len(result) > 0:
                    t_company = result[0].get('FID')

                    # cur.execute(f"update paidparking.temployee "
                    #             f"set FBlocked = 1 "
                    #             f"where FApacsID = {f_apacs_id} "
                    #             f"and FActivity = 1 "
                    #             f"and FCompanyID = {t_company}")
                    #
                    # result = cur.rowcount
                    result = 1  # TODO убрать при получении инструкций

                    if result == 1:
                        ret_value['status'] = "SUCCESS"
                    elif result > 1:
                        ret_value['status'] = "WARNING"
                        logger.add_log(f"ERROR\tCardHolder.block_card_holder\tОшибка! Обновлено больше одного пропуск: "
                                       f"f_apacs_id {f_apacs_id} user_id {login_id} inn {inn} company_id {t_company}")
                        ret_value['desc'] = "Было отменено несколько заявок"
                    else:
                        logger.add_log(f"WARNING\tCardHolder.block_card_holder\tНе удалось найти заявку: "
                                       f"f_apacs_id {f_apacs_id} user_id {login_id} inn {inn} company_id {t_company}")
                        ret_value['desc'] = "Не удалось заблокировать сотрудника"
                else:
                    ret_value['desc'] = "Не удалось найти компанию по ИНН"

            connection.commit()

        except Exception as ex:
            logger.add_log(f"ERROR\tCardHolder.block_card_holder\tОшибка связи с базой данных: {ex} "
                           f"(данные для заполнения: login_id {login_id} inn {inn} fid {f_apacs_id})")
            ret_value['desc'] = "Ошибка на сервере при попытке блокировки пропуска"

        return ret_value
