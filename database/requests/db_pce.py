""" PCE: Parking - Company - Employee """

from misc.logger import Logger
from database.db_connection import connect_db


class PCEConnectionDB:
    # Запрос для постоянных пропусков этап поиска сотрудников
    @staticmethod
    def find_employees(guid_company, logger: Logger):
        """ Функция возвращает список сотрудников привязанных к основному пользователю(компании) user_id_tguser"""

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                cur.execute(f"select temployee.* "
                            f"from paidparking.tcompany, paidparking.temployee "
                            f"where temployee.FCompanyID = tcompany.FID "
                            f"and tcompany.FGUID = '{guid_company}' "
                            f"order by FFavorite desc, FLastName, FName, FMiddleName")
                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'

                    # ret_result = list()
                    #
                    # # Меняем формат datetime в str
                    # for index in range(len(result)):
                    #     employee = dict()
                    #     employee['FCreateDate'] = str(result[index]['FCreateDate'])
                    #     employee['FLastDecreaseDate'] = str(result[index]['FLastDecreaseDate'])
                    #     employee['FLastModifyDate'] = str(result[index]['FLastModifyDate'])
                    #
                    #     employee['FName'] = f"{result[index]['FLastName']} {result[index]['FFirstName']} " \
                    #                         f"{result[index]['FMiddleName']}"
                    #
                    #     employee['FApacsID'] = result[index]['FApacsID']
                    #     employee['FFavorite'] = result[index]['FFavorite']
                    #
                    #     ret_result.append(employee)
                    #
                    # ret_value['data'] = ret_result

                    # Меняем формат datetime в str
                    for index in range(len(result)):
                        result[index]['FCreateDate'] = str(result[index]['FCreateDate'])
                        result[index]['FLastDecreaseDate'] = str(result[index]['FLastDecreaseDate'])
                        result[index]['FLastModifyDate'] = str(result[index]['FLastModifyDate'])

                    ret_value['data'] = result
                else:
                    ret_value['desc'] = f"Не удалось найти сотрудников компании guid: {guid_company}"

            connection.close()

        except Exception as ex:
            logger.add_log(f"ERROR\tPCEConnectionDB.find_employees\tОшибка связи с базой данных: {ex}")
            ret_value['desc'] = f"Ошибка связи с базой данных: {ex}"

        return ret_value

    # Запрос для постоянных пропусков этап поиска сотрудника
    @staticmethod
    def take_employee(guid, logger: Logger):
        """ Функция возвращает данные пользователя найденного по GUID """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                cur.execute(f"select FLastName, FFirstName, FMiddleName, FCompanyAccount, FPersonalAccount "
                            f"from paidparking.temployee where FGUID = '{guid}'")
                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'
                    ret_value['data'] = result
                else:
                    ret_value['desc'] = f'Не удалось найти сотрудника с FGUID = {guid}'

        except Exception as ex:
            logger.add_log(f"ERROR\tPCEConnectionDB.take_employee\tОшибка связи с базой данных: {ex}")
            ret_value['desc'] = f'Ошибка связи с базой данных'

        return ret_value

    # Запрос получения ИНН и имени организации пользователя
    @staticmethod
    def take_company(id_company, inn_company, logger: Logger) -> dict:
        """id компании и ИНН """
        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                cur.execute(f"select  tcompany.* "
                                f"from sac3.dept, sac3.user, paidparking.tcompany "
                                f"where ID_Dept = ID_Dept_user "
                                f"and FINN = INN_Dept "
                                f"and Active_User = 1 "
                                f"and login_user = {id_company} "
                                f"and INN_Dept = {inn_company}")
                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'

                    # Меняем формат datetime в str
                    result[0]['FCreateDate'] = str(result[0]['FCreateDate'])
                    result[0]['FLastModifyDate'] = str(result[0]['FLastModifyDate'])

                    ret_value['data'] = result
                else:
                    ret_value['desc'] = f"Не удалось найти компанию id: {id_company} inn: {inn_company}"

        except Exception as ex:
            logger.add_log(f"ERROR\tPCEConnectionDB.take_inn\tОшибка связи с базой данных: {ex}")
            ret_value['desc'] = f"Ошибка связи с базой данных: {ex}"

        return ret_value

    # Запрос для добавления п.е. сотруднику
    @staticmethod
    def add_point(guid, plus_units: int, logger: Logger):
        """ Функция принимает FGUID и кол-во П.Е. для списания """

        session_info = dict()

        session_info['status'] = 'ERROR'
        session_info['guid'] = guid
        session_info['take_off_point'] = plus_units
        session_info['desc'] = ''

        try:
            session_info['step_session'] = 0  # Ступени сессии для отчета ошибок
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                session_info['step_session'] = 1  # Ступени сессии для отчета ошибок
                # 1 Загружаем данные сотрудника

                cur.execute(f"select FCompanyAccount, FCompanyID, FGUID, FLastName "
                                  f"from paidparking.temployee "
                                  f"where FGUID = '{guid}'")

                result = cur.fetchone()

                session_info['empl_first_account'] = int(result['FCompanyAccount'])
                session_info['f_company_id'] = result['FCompanyID']
                session_info['fguid_employee'] = result['FGUID']
                session_info['empl_last_name'] = result['FLastName']

                session_info['step_session'] = 2  # Ступени сессии для отчета ошибок

                # 2 Загружаем данные компании

                cur.execute(f"select FAccount, FGUID, FName "
                                  f"from paidparking.tcompany "
                                  f"where FID = {session_info['f_company_id']}")

                result = cur.fetchone()

                session_info['fguid_company'] = result['FGUID']
                session_info['comp_old_account'] = result['FAccount']
                session_info['comp_name'] = result['FName']

                session_info['step_session'] = 3  # Ступени сессии для отчета ошибок

                # 3 Меняем данные если это допустимо условием
                if session_info['comp_old_account'] >= plus_units:
                    # Добавляем п.е. сотруднику
                    session_info['step_session'] = 3.1  # Ступени сессии для отчета ошибок
                    cur.execute(f"update paidparking.temployee "
                                      f"set FCompanyAccount = FCompanyAccount + {plus_units} "
                                      f"where FGUID = '{guid}'")
                    session_info['step_session'] = 3.2  # Ступени сессии для отчета ошибок
                    # Списываем п.е. компании
                    cur.execute(f"update paidparking.tcompany "
                                      f"set FAccount = FAccount - {plus_units} "
                                      f"where FID = {session_info['f_company_id']}")

                    connection.commit()

                    session_info['step_session'] = 4  # Ступени сессии для отчета ошибок
                    # 4 Загружаем баланс сотрудника

                    cur.execute(f"select FCompanyAccount "
                                      f"from paidparking.temployee "
                                      f"where FGUID = '{guid}'")

                    result = cur.fetchone()
                    session_info['empl_end_account'] = int(result['FCompanyAccount'])

                    session_info['step_session'] = 5  # Ступени сессии для отчета ошибок
                    # 5 Загружаем баланс компании

                    cur.execute(f"select FAccount, FGUID, FName "
                                      f"from paidparking.tcompany "
                                      f"where FID = {session_info['f_company_id']}")

                    result = cur.fetchone()
                    session_info['comp_new_account'] = result['FAccount']

                    if session_info['empl_first_account'] != session_info['empl_end_account']:

                        session_info['step_session'] = 6.1  # Ступени сессии для отчета ошибок
                        # 6.1 Записываем отчет транзакции
                        cur.execute(f"insert into paidparking.ttransaction "
                                          f"(FTime, FTTypeTransactionID, FGUIDFrom, FGUIDTo, FValue) "
                                          f"VALUES (now(), 10, '{session_info['fguid_company']}', "
                                          f"'{session_info['fguid_employee']}', {plus_units})")
                        connection.commit()

                        session_info['status'] = 'SUCCESS'

                    else:
                        session_info['step_session'] = 6.2  # Ступени сессии для отчета ошибок
                        # 6.2 Записываем отчет транзакции
                        logger.add_log(f"ERROR\tPCEConnectionDB.add_point\tОшибка связи с базой данных: {session_info}")

                else:
                    session_info['desc'] = "Недостаточно средств для списания"

            # 7 Закрытие связи с базой
            session_info['step_session'] = 7
            connection.close()

        except Exception as ex:
            logger.add_log(f"ERROR\tPCEConnectionDB.add_point\tОшибка связи с базой данных: {ex}\n"
                           f"desc: {session_info}")

        return session_info

    # Запрос для списания п.е. у сотрудника
    @staticmethod
    def remove_point(guid, take_off_units: int, logger: Logger):
        """ Функция принимает FGUID и кол-во П.Е. для списания """

        session_info = dict()

        session_info['status'] = 'ERROR'
        session_info['guid'] = guid
        session_info['take_off_point'] = take_off_units
        session_info['desc'] = ''

        try:
            session_info['step_session'] = 0  # Ступени сессии для отчета ошибок
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                session_info['step_session'] = 1  # Ступени сессии для отчета ошибок
                # 1 Загружаем данные сотрудника
                cur.execute(f"select FCompanyAccount, FCompanyID, FGUID, FLastName "
                                  f"from paidparking.temployee "
                                  f"where FGUID = '{guid}'")

                result = cur.fetchone()

                session_info['empl_first_account'] = int(result['FCompanyAccount'])
                session_info['f_company_id'] = result['FCompanyID']
                session_info['fguid_employee'] = result['FGUID']
                session_info['empl_last_name'] = result['FLastName']

                session_info['step_session'] = 2  # Ступени сессии для отчета ошибок
                # 2 Загружаем данные компании
                cur.execute(f"select FAccount, FGUID, FName "
                                  f"from paidparking.tcompany "
                                  f"where FID = {session_info['f_company_id']}")

                result = cur.fetchone()

                session_info['fguid_company'] = result['FGUID']
                session_info['comp_old_account'] = result['FAccount']
                session_info['comp_name'] = result['FName']

                session_info['step_session'] = 3  # Ступени сессии для отчета ошибок

                # 3 Меняем данные если это допустимо условием
                if session_info['empl_first_account'] >= take_off_units:
                    # Списываем п.е. с сотрудника
                    session_info['step_session'] = 3.1  # Ступени сессии для отчета ошибок
                    cur.execute(f"update paidparking.temployee "
                                      f"set FCompanyAccount = FCompanyAccount - {take_off_units} "
                                      f"where FGUID = '{guid}'")
                    session_info['step_session'] = 3.2  # Ступени сессии для отчета ошибок
                    # Добавляем п.е. в компанию
                    cur.execute(f"update paidparking.tcompany "
                                      f"set FAccount = FAccount + {take_off_units} "
                                      f"where FID = {session_info['f_company_id']}")

                    connection.commit()

                    session_info['step_session'] = 4  # Ступени сессии для отчета ошибок
                    # 4 Загружаем баланс сотрудника
                    cur.execute(f"select FCompanyAccount "
                                      f"from paidparking.temployee "
                                      f"where FGUID = '{guid}'")

                    result = cur.fetchone()
                    session_info['empl_end_account'] = int(result['FCompanyAccount'])

                    session_info['step_session'] = 5  # Ступени сессии для отчета ошибок
                    # 5 Загружаем баланс компании
                    cur.execute(f"select FAccount, FGUID, FName "
                                      f"from paidparking.tcompany "
                                      f"where FID = {session_info['f_company_id']}")

                    result = cur.fetchone()
                    session_info['comp_new_account'] = result['FAccount']

                    if session_info['empl_first_account'] != session_info['empl_end_account']:

                        session_info['step_session'] = 6.1  # Ступени сессии для отчета ошибок
                        # 6.1 Записываем отчет транзакции
                        cur.execute(f"insert into paidparking.ttransaction "
                                          f"(FTime, FTTypeTransactionID, FGUIDFrom, FGUIDTo, FValue) "
                                          f"VALUES (now(), 11, '{session_info['fguid_employee']}', "
                                          f"'{session_info['fguid_company']}', {take_off_units})")
                        connection.commit()

                        session_info['status'] = 'SUCCESS'
                    else:
                        # 6.2 Записываем отчет транзакции
                        session_info['step_session'] = 6.2  # Ступени сессии для отчета ошибок

                        logger.add_log(f"ERROR\tPCEConnectionDB.remove_point\t"
                                       f"Ошибка связи с базой данных: {session_info}")

                else:
                    session_info['desc'] = "Недостаточно средств для списания"

            # 7 Закрытие связи с базой
            session_info['step_session'] = 7
            connection.close()

        except Exception as ex:
            logger.add_log(f"ERROR\tPCEConnectionDB.remove_point\tОшибка связи с базой данных: {ex}\n"
                           f"desc: {session_info}")

        return session_info
