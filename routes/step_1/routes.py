""" Этап разработки 1 """
from flask import Blueprint, request, jsonify
from misc.consts import ALLOW_IP, LOGGER, ERROR_ACCESS_IP, ERROR_READ_REQUEST

from misc.take_uid import UserUid

from database.requests.db_pce import PCEConnectionDB
from database.requests.db_transaction import TransactionDB
from database.requests.db_decrease import DecreaseDB
from database.requests.db_employee import EmployeeDB

step1 = Blueprint('step1', __name__)

# STEP 1


# ИНФОРМАЦИЯ о КОМПАНИИ
@step1.route('/RequestCompany', methods=['GET'])
def company_information():
    """ Принимает id и ИНН компании и возвращает информацию о балансе компании """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tRequestCompany\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args

        inn_company = res_request.get('InnCompany')
        id_company = res_request.get('IDCompany')

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tRequestCompany\tПолучены данные: "
                       f"(InnCompany: {inn_company} IDCompany: {id_company})", print_it=False)

        if inn_company:
            result_db = PCEConnectionDB.take_company(id_company, inn_company, LOGGER)

            if result_db['status'] == 'SUCCESS':

                json_replay['DATA'] = result_db['data'][0]
                json_replay['RESULT'] = 'SUCCESS'

            else:
                json_replay['DESC'] = result_db['desc']
        else:
            # Если в запросе нет данных
            LOGGER.add_log(f"ERROR\tRequestCompany\tОшибка чтения request: В запросе нет данных")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)


@step1.route('/RequestEmployees', methods=['GET'])
def employees_list():
    """ Принимает GUID компании и возвращает информацию список сотрудников компании """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tRequestEmployees\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args
        guid_company = res_request.get('GUIDCompany')

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tRequestEmployees\tПолучены данные: "
                       f"(GUIDCompany: {guid_company})", print_it=False)

        if guid_company:
            result_db = PCEConnectionDB.find_employees(guid_company, LOGGER)

            if result_db['status'] == 'SUCCESS':

                json_replay['DATA'] = result_db['data']
                json_replay['RESULT'] = 'SUCCESS'

            else:
                json_replay['DESC'] = result_db['desc']
        else:
            # Если в запросе нет данных
            LOGGER.add_log(f"ERROR\tRequestEmployees\tОшибка чтения request: В запросе нет данных")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)


@step1.route('/RequestCompanyTransaction', methods=['GET'])
def company_transaction():
    """ Принимает FGUID компании и возвращает информацию о всех транзакция """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tRequestTransaction\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args
        duration = dict()

        duration['data_from'] = res_request.get('data_from')
        duration['data_to'] = res_request.get('data_to')
        guid = res_request.get('guid')

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tRequestTransaction\tПолучены данные: "
                       f"(data_from: {duration['data_from']} data_to: {duration['data_to']} guid: {guid})",
                       print_it=False)

        if guid:
            result_db = TransactionDB.take_company(guid, duration, LOGGER)

            if result_db['status'] == 'SUCCESS':

                json_replay['DATA'] = result_db['data']
                json_replay['RESULT'] = 'SUCCESS'

            else:
                json_replay['DESC'] = result_db['desc']
        else:
            # Если в запросе нет данных
            LOGGER.add_log(f"ERROR\tRequestCompanyTransaction\tОшибка чтения request: В запросе нет данных")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)

# РЕДАКТОР СОТРУДНИКА


# СОТРУДНИК и АВТОМОБИЛЬ
@step1.route('/SetCarEmployee', methods=['GET'])
def set_employee_car():
    """ Принимает GUID сотрудника и номер автомобиля который нужно к нему привязать """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tSetCarEmployee\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args

        guid = str(res_request.get('guid'))
        car_number = str(res_request.get('car_number'))

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tSetCarEmployee\tПолучены данные: "
                       f"(car_number: {car_number} guid: {guid})",
                       print_it=False)

        # изменяем номер в нужный формат
        car_number = car_number.upper()

        for it in (' ', '/', '.', '-'):
            car_number = car_number.replace(it, '')

        if guid:

            result_db = EmployeeDB.set_car_number(guid, car_number, LOGGER)

            if result_db['status'] == 'SUCCESS':

                json_replay['DATA'] = result_db['data']
                json_replay['RESULT'] = 'SUCCESS'

            else:
                json_replay['DESC'] = result_db['desc']
        else:
            # Если в запросе нет данных
            LOGGER.add_log(f"ERROR\tSetCarEmployee\tОшибка чтения request: В запросе нет данных")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)


@step1.route('/RemoveCarEmployee', methods=['GET'])
def remove_employee_car():
    """ Принимает GUID сотрудника и номер авто который нужно удалить """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tRemoveCarEmployee\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args

        guid = str(res_request.get('guid'))
        f_plate_id = str(res_request.get('fplateid'))

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tRemoveCarEmployee\tПолучены данные: "
                       f"(fplateid: {f_plate_id} guid: {guid})",
                       print_it=False)

        if guid:

            result_db = EmployeeDB.remove_car_number(guid, f_plate_id, LOGGER)

            if result_db['status'] == 'SUCCESS':

                json_replay['DATA'] = result_db['data']
                json_replay['RESULT'] = 'SUCCESS'
                json_replay['DESC'] = result_db['desc']

            else:
                json_replay['DESC'] = result_db['desc']
        else:
            # Если в запросе нет данных
            LOGGER.add_log(f"ERROR\tRemoveCarEmployee\tОшибка чтения request: В запросе нет данных")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)


@step1.route('/RequestCarsEmployee', methods=['GET'])
def get_employee_cars():
    """ Принимает GUID сотрудника и возвращает номера машин привязанных к нему """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tSetContacts\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args

        guid = res_request.get('guid')

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tRequestCarsEmployee\tПолучены данные: "
                       f"(guid: {guid})",
                       print_it=False)

        if guid:

            result_db = EmployeeDB.get_car_numbers(guid, LOGGER)

            if result_db['status'] == 'SUCCESS':

                json_replay['DATA'] = result_db['data']
                json_replay['RESULT'] = 'SUCCESS'

            else:
                json_replay['DESC'] = result_db['desc']
        else:
            # Если в запросе нет данных
            LOGGER.add_log(f"ERROR\tSetContacts\tОшибка чтения request: В запросе нет данных")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)


# СОТРУДНИК

@step1.route('/GetEmployeeInfo', methods=['GET'])
def employee_info():
    """ Принимает FGUID сотрудника, возвращает данные сотрудника """

    ret_value = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tGetEmployeeInfo\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        ret_value["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args

        guid = res_request.get('guid')
        uid = res_request.get('uid')

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tGetEmployeeInfo\tПолучены данные: "
                       f"(guid: {guid}, uid: {uid})",
                       print_it=False)

        try:
            if guid:  # Получаем данные сотрудника по FGUID
                req_text = f"FGUID = '{guid}'"
                ret_value = EmployeeDB.take_employee_info(req_text, LOGGER)
            elif uid:  # Если нет FGUID тогда проверяем наличие UID и по нему делаем запрос
                fid_apacs = UserUid.reverse_uid(int(uid))
                req_text = f"FID = {fid_apacs['FID']} and FApacsID = {fid_apacs['FApacsID']}"
                ret_value = EmployeeDB.take_employee_info(req_text, LOGGER)
            else:
                # Если в запросе нет данных
                LOGGER.add_log(f"ERROR\tGetEmployeeInfo\tОшибка чтения request: В запросе нет данных")
                ret_value["DESC"] = ERROR_READ_REQUEST
        except Exception as ex:
            LOGGER.add_log(f"ERROR\tGetEmployeeInfo\tИсключение вызвало: {ex}")
            ret_value["DESC"] = ERROR_READ_REQUEST

    return jsonify(ret_value)


@step1.route('/SetContacts', methods=['GET'])
def employee_contacts():
    """ Принимает GUID сотрудника, номер телефона, email\n
    так же можно указывать один из двух параметров phone/email """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tSetContacts\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args

        guid = res_request.get('guid')
        phone = res_request.get('phone')
        email = res_request.get('email')

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tSetContacts\tПолучены данные: "
                       f"(guid: {guid} phone: {phone} email: {email})",
                       print_it=False)

        if guid:
            result_db = dict()

            if phone and email:
                result_db = EmployeeDB.add_phone_email(guid, phone, email, LOGGER)
            elif phone:
                result_db = EmployeeDB.add_phone(guid, phone, LOGGER)
            elif email:
                result_db = EmployeeDB.add_email(guid, email, LOGGER)
            else:
                result_db['status'] = "ERROR"
                result_db['desc'] = "Ошибка. Должна быть хотя бы одна переменная phone или email"

            if result_db['status'] == 'SUCCESS':

                json_replay['DATA'] = result_db['data']
                json_replay['RESULT'] = 'SUCCESS'

            else:
                json_replay['DESC'] = result_db['desc']
        else:
            # Если в запросе нет данных
            LOGGER.add_log(f"ERROR\tSetContacts\tОшибка чтения request: В запросе нет данных")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)


@step1.route('/SetFavorite', methods=['GET'])
def employee_favorite():
    """ Принимает GUID сотрудника и значение is_favorite где может быть 1 или 0 """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tSetFavorite\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args

        guid = res_request.get('guid')

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tSetFavorite\tПолучены данные: "
                       f"(guid: {guid})",
                       print_it=False)

        try:
            is_favorite = int(res_request.get('is_favorite'))
        except Exception as ex:
            LOGGER.add_log(f"ERROR\tSetFavorite\tОшибка чтения request: В запросе {ex}")
            is_favorite = 173317

        if guid and 0 <= is_favorite <= 1:

            result_db = EmployeeDB.set_favorite(guid, is_favorite, LOGGER)

            if result_db['status'] == 'SUCCESS':
                json_replay['RESULT'] = 'SUCCESS'
            else:
                json_replay['DESC'] = result_db['desc']
        else:
            # Если в запросе нет данных
            if is_favorite != 173317:
                LOGGER.add_log(f"ERROR\tSetFavorite\tОшибка чтения request: "
                               f"В запросе guid: {guid} is_favorite: {is_favorite}")
            json_replay["DESC"] = "Ошибка. is_favorite может быть только 1 или 0"

    return jsonify(json_replay)


# Метод связан с проектом телеграм
@step1.route('/AddAccount', methods=['GET'])
def employee_add_account():
    """ Принимает FGUID сотрудника и кол-во п.е. """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tAddAccount\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args
        guid = res_request.get('guid')
        units = int(res_request.get('units'))

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tAddAccount\tПолучены данные: "
                       f"(guid: {guid} units: {units})",
                       print_it=False)

        if guid and units:
            result_db = PCEConnectionDB.add_point(guid, units, LOGGER)

            if result_db['status'] == 'SUCCESS':
                json_replay['RESULT'] = 'SUCCESS'
            else:
                json_replay['DESC'] = result_db['desc']

        else:
            # Если в запросе нет данных
            LOGGER.add_log(f"ERROR\tAddAccount\tОшибка чтения request: В запросе нет числа или GUID")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)


# Метод связан с проектом телеграм
@step1.route('/RemoveAccount', methods=['GET'])
def employee_remove_account():
    """ Принимает FGUID сотрудника и кол-во п.е. """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tRemoveAccount\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args

        guid = res_request.get('guid')
        units = int(res_request.get('units'))

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tRemoveAccount\tПолучены данные: "
                       f"(guid: {guid} units: {units})",
                       print_it=False)

        if guid and units:
            result_db = PCEConnectionDB.remove_point(guid, units, LOGGER)

            if result_db['status'] == 'SUCCESS':
                json_replay['RESULT'] = 'SUCCESS'
            else:
                json_replay['DESC'] = result_db['desc']

        else:
            # Если в запросе нет данных
            LOGGER.add_log(f"ERROR\tRemoveAccount\tОшибка чтения request: В запросе нет числа или GUID")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)


@step1.route('/RequestTransaction', methods=['GET'])
def employee_transaction():
    """ Принимает FGUID сотрудника, период и возвращает информацию о всех транзакция с его счета """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tRequestTransaction\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args
        duration = dict()

        duration['data_from'] = res_request.get('data_from')
        duration['data_to'] = res_request.get('data_to')
        guid = res_request.get('guid')

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tRequestTransaction\tПолучены данные: "
                       f"(guid: {guid} data_from: {duration['data_from']} data_to: {duration['data_to']})",
                       print_it=False)

        if guid:
            result_db = TransactionDB.take_employee(guid, duration, LOGGER)

            if result_db['status'] == 'SUCCESS':

                json_replay['DATA'] = result_db['data']
                json_replay['RESULT'] = 'SUCCESS'

            else:
                json_replay['DESC'] = result_db['desc']
        else:
            # Если в запросе нет данных
            LOGGER.add_log(f"ERROR\tRequestTransaction\tОшибка чтения request: В запросе нет данных")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)


@step1.route('/RequestDecrease', methods=['GET'])
def employee_decrease():
    """ Принимает FGUID сотрудника и возвращает информацию о всех списаниях с его счета """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tRequestDecrease\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        res_request = request.args
        duration = dict()

        duration['data_from'] = res_request.get('data_from')
        duration['data_to'] = res_request.get('data_to')
        guid = res_request.get('guid')

        # Лог всех входных данных запроса
        LOGGER.add_log(f"EVENT\tRequestDecrease\tПолучены данные: "
                       f"(guid: {guid} data_from: {duration['data_from']} data_to: {duration['data_to']})",
                       print_it=False)

        if guid:
            result_db = DecreaseDB.take(guid, duration, LOGGER)

            if result_db['status'] == 'SUCCESS':

                json_replay['DATA'] = result_db['data']
                json_replay['RESULT'] = 'SUCCESS'

            else:
                json_replay['DESC'] = result_db['desc']
        else:
            # Если в запросе нет данных
            LOGGER.add_log(f"ERROR\tRequestDecrease\tОшибка чтения request: В запросе нет данных")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)
