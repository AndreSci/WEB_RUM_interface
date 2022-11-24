""" PCE: Parking - Company - Employee """

from misc.logger import Logger
from database.db_connection import connect_db


class PCEConnectionDB:
    # Запрос для постоянных пропусков этап поиска сотрудников
    @staticmethod
    def find_employees(user_id_tguser, logger: Logger):
        """ Функция возвращает список сотрудников привязанных к основному пользователю(компании)"""

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                cur.execute(f"select FLastName, FFirstName, FMiddleName, tcompany.FName, tcompany.FINN, "
                                  f"tcompany.FApacsID as ApacsID_Comp, UserID_TGUser, "
                                  f"temployee.FApacsID as ApacsID_Emp "
                                  f"from paidparking.temployee, paidparking.tcompany, "
                                  f"sac3.dept, sac3.user, sac3.tguser "
                                  f"where temployee.FCompanyID = tcompany.FID "
                                  f"and tcompany.FINN = dept.INN_Dept "
                                  f"and ID_Dept_user = ID_Dept "
                                  f"and ID_User_TGUser = ID_User "
                                  f"and UserID_TGUser = {user_id_tguser}")
                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'
                    ret_value['data'] = result

            connection.close()

        except Exception as ex:
            logger.add_log(f"ERROR\tPCEConnectionDB.find_employees\tОшибка связи с базой данных: {ex}")

        return ret_value

    # Запрос для постоянных пропусков этап поиска сотрудника
    @staticmethod
    def take_employee(f_apacs_id, logger: Logger):
        """ Функция возвращает данные пользователя найденного по Apacs id """

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                cur.execute(f"select FLastName, FFirstName, FMiddleName, FCompanyAccount, FPersonalAccount "
                            f"from paidparking.temployee where FApacsID = '{f_apacs_id}'")
                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'
                    ret_value['data'] = result
                else:
                    ret_value['desc'] = f'Не удалось найти сотрудника с FAID = {f_apacs_id}'

        except Exception as ex:
            logger.add_log(f"ERROR\tPCEConnectionDB.take_employee\tОшибка связи с базой данных: {ex}")
            ret_value['desc'] = f'Ошибка связи с базой данных'

        return ret_value

    # Запрос получения ИНН и имени организации пользователя
    @staticmethod
    def take_inn(user_id_tguser, logger: Logger):

        ret_value = {"status": "ERROR", "desc": '', "data": list()}

        try:
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                cur.execute(f"select INN_Dept, Name_Dept, FID, FAccount "
                                  f"from sac3.dept, sac3.user, sac3.tguser, paidparking.tcompany "
                                  f"where UserID_TGUser = '{user_id_tguser}' "
                                  f"and ID_User = ID_User_TGUser "
                                  f"and ID_Dept = ID_Dept_user "
                                  f"and FINN = INN_Dept "
                                  f"and Active_User = 1 "
                                  f"and Active_TGUser = 1 ")
                result = cur.fetchall()

                if len(result) > 0:
                    ret_value['status'] = 'SUCCESS'
                    ret_value['data'] = result

        except Exception as ex:
            logger.add_log(f"ERROR\tPCEConnectionDB.take_inn\tОшибка связи с базой данных: {ex}")

        return ret_value

    # Запрос для добавления п.е. сотруднику
    @staticmethod
    def add_point(f_apacs_id, plus_point: int, logger: Logger):
        """ Функция принимает FApacsID и кол-во П.Е. для списания """

        session_info = dict()

        session_info['status'] = 'ERROR'
        session_info['f_apacs_id'] = f_apacs_id
        session_info['take_off_point'] = plus_point

        try:
            session_info['step_session'] = 0  # Ступени сессии для отчета ошибок
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                session_info['step_session'] = 1  # Ступени сессии для отчета ошибок
                # 1 Загружаем данные сотрудника

                cur.execute(f"select FCompanyAccount, FCompanyID, FGUID, FLastName "
                                  f"from paidparking.temployee "
                                  f"where FApacsID = {f_apacs_id}")

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

                if session_info['comp_old_account'] >= plus_point:
                    # Добавляем п.е. сотруднику
                    session_info['step_session'] = 3.1  # Ступени сессии для отчета ошибок
                    cur.execute(f"update paidparking.temployee "
                                      f"set FCompanyAccount = FCompanyAccount + {plus_point} "
                                      f"where FApacsID = {f_apacs_id}")
                    session_info['step_session'] = 3.2  # Ступени сессии для отчета ошибок
                    # Списываем п.е. компании
                    cur.execute(f"update paidparking.tcompany "
                                      f"set FAccount = FAccount - {plus_point} "
                                      f"where FID = {session_info['f_company_id']}")

                    connection.commit()

                session_info['step_session'] = 4  # Ступени сессии для отчета ошибок
                # 4 Загружаем баланс сотрудника

                cur.execute(f"select FCompanyAccount "
                                  f"from paidparking.temployee "
                                  f"where FApacsID = {f_apacs_id}")

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
                                      f"VALUES (now(), 18, '{session_info['fguid_company']}', "
                                      f"'{session_info['fguid_employee']}', {plus_point})")
                    connection.commit()

                    session_info['status'] = 'SUCCESS'

                else:
                    session_info['step_session'] = 6.2  # Ступени сессии для отчета ошибок
                    # 6.2 Записываем отчет транзакции
                    logger.add_log(f"ERROR\tPCEConnectionDB.add_point\tОшибка связи с базой данных: {session_info}")

            # 7 Закрытие связи с базой
            session_info['step_session'] = 7
            connection.close()

        except Exception as ex:
            logger.add_log(f"ERROR\tPCEConnectionDB.add_point\tОшибка связи с базой данных: {ex}\n"
                           f"desc: {session_info}")

        return session_info

    # Запрос для списания п.е. у сотрудника
    @staticmethod
    def remove_point(f_apacs_id, take_off_point: int, logger: Logger):
        """ Функция принимает FApacsID и кол-во П.Е. для списания """

        session_info = dict()

        session_info['status'] = 'ERROR'
        session_info['f_apacs_id'] = f_apacs_id
        session_info['take_off_point'] = take_off_point

        try:
            session_info['step_session'] = 0  # Ступени сессии для отчета ошибок
            # Создаем подключение
            connection = connect_db(logger)

            with connection.cursor() as cur:
                session_info['step_session'] = 1  # Ступени сессии для отчета ошибок
                # 1 Загружаем данные сотрудника
                cur.execute(f"select FCompanyAccount, FCompanyID, FGUID, FLastName "
                                  f"from paidparking.temployee "
                                  f"where FApacsID = {f_apacs_id}")

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
                if session_info['empl_first_account'] >= take_off_point:
                    # Списываем п.е. с сотрудника
                    session_info['step_session'] = 3.1  # Ступени сессии для отчета ошибок
                    cur.execute(f"update paidparking.temployee "
                                      f"set FCompanyAccount = FCompanyAccount - {take_off_point} "
                                      f"where FApacsID = {f_apacs_id}")
                    session_info['step_session'] = 3.2  # Ступени сессии для отчета ошибок
                    # Добавляем п.е. в компанию
                    cur.execute(f"update paidparking.tcompany "
                                      f"set FAccount = FAccount + {take_off_point} "
                                      f"where FID = {session_info['f_company_id']}")

                    connection.commit()

                session_info['step_session'] = 4  # Ступени сессии для отчета ошибок
                # 4 Загружаем баланс сотрудника
                cur.execute(f"select FCompanyAccount "
                                  f"from paidparking.temployee "
                                  f"where FApacsID = {f_apacs_id}")

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
                                      f"VALUES (now(), 19, '{session_info['fguid_employee']}', "
                                      f"'{session_info['fguid_company']}', {take_off_point})")
                    connection.commit()

                    session_info['status'] = 'SUCCESS'
                else:
                    # 6.2 Записываем отчет транзакции
                    session_info['step_session'] = 6.2  # Ступени сессии для отчета ошибок

                    logger.add_log(f"ERROR\tPCEConnectionDB.remove_point\tОшибка связи с базой данных: {session_info}")

            # 7 Закрытие связи с базой
            session_info['step_session'] = 7
            connection.close()

        except Exception as ex:
            logger.add_log(f"ERROR\tPCEConnectionDB.remove_point\tОшибка связи с базой данных: {ex}\n"
                           f"desc: {session_info}")

        return session_info