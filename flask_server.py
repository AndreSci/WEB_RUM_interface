from flask import Flask, render_template, request, make_response, jsonify
import requests
import time

from misc.utility import SettingsIni
from misc.logger import Logger
from misc.allow_ip import AllowedIP, ip_control

from database.requests.db_pce import PCEConnectionDB
from database.requests.db_transaction import TransactionDB
from database.requests.db_decrease import DecreaseDB
from database.requests.db_employee import EmployeeDB


ERROR_ACCESS_IP = 'access_block_ip'
ERROR_READ_REQUEST = 'error_read_request'
ERROR_ON_SERVER = 'server_error'

OLD_MODE = 0


def web_flask(logger: Logger, settings_ini: SettingsIni):
    """ Главная функция создания сервера Фласк. """

    app = Flask(__name__)  # Объявление сервера

    app.config['JSON_AS_ASCII'] = False

    # Блокируем сообщения фласк
    # block_flask_logs()

    set_ini = settings_ini.take_settings()

    # Для передачи данных в старом стиле сайта
    global OLD_MODE
    OLD_MODE = set_ini['old_mode']

    allow_ip = AllowedIP()
    allow_ip.read_file(logger)

    logger.add_log(f"SUCCESS\tweb_flask\tСервер WEB_RUM_Flask начал свою работу")  # log

    # IP FUNCTION

    @app.route('/DoAddIp', methods=['POST'])
    def add_ip():
        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}
        print("HELLO IP TEST")
        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tDoAddIp\tзапрос от ip: {user_ip}")

        if not allow_ip.find_ip(user_ip, logger, 2):  # Устанавливаем activity_lvl=2 для проверки уровня доступа
            json_replay["DESC"] = "Ошибка доступа по IP"
        else:

            if request.is_json:
                json_request = request.json

                new_ip = json_request.get("ip")
                activity = int(json_request.get("activity"))

                allow_ip.add_ip(new_ip, logger, activity)

                json_replay["RESULT"] = "SUCCESS"
                json_replay["DESC"] = f"IP - {new_ip} добавлен с доступом {activity}"
            else:
                logger.add_log(f"ERROR\tDoCreateGuest\tНе удалось прочитать Json из request")
                json_replay["DESC"] = "Ошибка. Не удалось прочитать Json из request."

        return jsonify(json_replay)

    # MAIN FUNCTION

    # - COMPANY

    @app.route('/RequestCompany', methods=['POST'])
    def company_information():
        """ Принимает id компании и возвращает информацию о балансе компании и список сотрудников компании """

        if int(OLD_MODE) == 1:  # старый вариант передачи данных
            json_replay = {"Result": "ERROR", "DESC": ""}

        else:   # новый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tRequestCompany\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args

            inn_company = res_request.get('InnCompany')
            id_company = res_request.get('IDCompany')

            if inn_company:
                result_db = PCEConnectionDB.take_company(id_company, inn_company, logger)

                if result_db['status'] == 'SUCCESS':

                    # старый вариант передачи данных
                    if int(OLD_MODE) == 1:
                        json_replay['Result'] = 'SUCCESS'

                        json_replay['GUID'] = result_db['data'][0].get('FGUID')
                        json_replay['Name'] = result_db['data'][0].get('FName')
                    else:
                        # Новый вариант
                        json_replay['DATA'] = result_db['data'][0]
                        json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tRequestCompany\tошибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RequestEmployees', methods=['POST'])
    def employees_list():
        """ Принимает id компании и возвращает информацию о балансе компании и список сотрудников компании """

        if int(OLD_MODE) == 1:  # старый вариант передачи данных
            json_replay = {"Result": "ERROR", "DESC": ""}

        else:   # новый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tRequestEmployees\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args
            guid_company = res_request.get('GUIDCompany')

            if guid_company:
                result_db = PCEConnectionDB.find_employees(guid_company, logger)

                if result_db['status'] == 'SUCCESS':

                    # старый вариант передачи данных
                    if int(OLD_MODE) == 1:
                        json_replay['Result'] = 'SUCCESS'

                        index_employee = 1

                        for it in result_db['data']:
                            json_replay[f'Employee{index_employee}'] = it
                            index_employee += 1

                        json_replay["EmployeeCount"] = str(len(result_db['data']))
                    else:
                        # Новый вариант
                        json_replay['DATA'] = result_db['data']
                        json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tRequestEmployees\tошибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RequestCompanyTransaction', methods=['POST'])
    def company_transaction():
        """ Принимает FGUID компании и возвращает информацию о всех транзакция """

        if int(OLD_MODE) == 1:  # старый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": ""}

        else:  # новый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tRequestTransaction\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args
            duration = dict()

            duration['data_from'] = res_request.get('data_from')
            duration['data_to'] = res_request.get('data_to')
            guid = res_request.get('guid')

            if guid:
                result_db = TransactionDB.take_company(guid, duration, logger)

                if result_db['status'] == 'SUCCESS':

                    # старый вариант передачи данных
                    if int(OLD_MODE) == 1:
                        json_replay['RESULT'] = 'SUCCESS'
                        json_replay['DATA'] = result_db['data']

                    else:
                        # Новый вариант
                        json_replay['DATA'] = result_db['data']
                        json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tRequestCompanyTransaction\tошибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    # - EMPLOYEE

    @app.route('/SetContacts', methods=['POST'])
    def employee_contacts():
        """ Принимает GUID сотрудника, номер телефона, email и возвращает информацию о сотруднике с изменениями \n
        можно указывать один из двух параметров phone/email """

        if int(OLD_MODE) == 1:  # старый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": ""}

        else:  # новый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tSetContacts\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args

            guid = res_request.get('guid')
            phone = res_request.get('phone')
            email = res_request.get('email')

            if guid:
                result_db = dict()

                if phone and email:
                    result_db = EmployeeDB.add_phone_email(guid, phone, email, logger)
                elif phone:
                    result_db = EmployeeDB.add_phone(guid, phone, logger)
                elif email:
                    result_db = EmployeeDB.add_email(guid, email, logger)
                else:
                    result_db['status'] = "ERROR"
                    result_db['desc'] = "Ошибка. Должна быть хотя бы одна переменная phone или email"

                if result_db['status'] == 'SUCCESS':

                    # старый вариант передачи данных
                    if int(OLD_MODE) == 1:
                        json_replay['RESULT'] = 'SUCCESS'
                        json_replay['DATA'] = result_db['data']

                    else:
                        # Новый вариант
                        json_replay['DATA'] = result_db['data']
                        json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tSetContacts\tошибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/SetFavorite', methods=['POST'])
    def employee_favorite():
        """ Принимает GUID сотрудника и значение is_favorite где может быть 1 или 0 """

        if int(OLD_MODE) == 1:  # старый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": ""}

        else:  # новый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tSetFavorite\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args

            guid = res_request.get('guid')
            try:
                is_favorite = int(res_request.get('is_favorite'))
            except Exception as ex:
                logger.add_log(f"ERROR\tSetFavorite\tошибка чтения request: В запросе нет данных {ex}")
                is_favorite = 'None'

            if guid and type(is_favorite) == int:
                result_db = dict()

                # Проверяем входные данные и отправляем запрос в БД
                if is_favorite == 1 or is_favorite == 0:
                    result_db = EmployeeDB.set_favorite(guid, is_favorite, logger)
                else:
                    result_db['status'] = "ERROR"
                    result_db['desc'] = "Ошибка. is_favorite может быть только 1 или 0"

                if result_db['status'] == 'SUCCESS':
                    json_replay['RESULT'] = 'SUCCESS'
                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tSetFavorite\tошибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/AddAccount', methods=['POST'])
    def employee_add_account():
        """ Принимает FGUID сотрудника и кол-во п.е. """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tAddAccount\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            json_request = request.json
            guid = json_request.get('guid')
            units = json_request.get('units')

            if guid and type(units) == int:
                result_db = PCEConnectionDB.add_point(guid, units, logger)

                if result_db['status'] == 'SUCCESS':
                    json_replay['RESULT'] = 'SUCCESS'
                else:
                    json_replay['DESC'] = result_db['desc']

            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tAddAccount\tошибка чтения Json: В запросе нет Json")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RemoveAccount', methods=['POST'])
    def employee_remove_account():
        """ Принимает FGUID сотрудника и кол-во п.е. """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tRemoveAccount\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            json_request = request.json
            guid = json_request.get('guid')
            units = json_request.get('units')

            if guid and type(units) == int:
                result_db = PCEConnectionDB.remove_point(guid, units, logger)

                if result_db['status'] == 'SUCCESS':
                    json_replay['RESULT'] = 'SUCCESS'
                else:
                    json_replay['DESC'] = result_db['desc']

            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tRemoveAccount\tошибка чтения Json: В запросе нет Json")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/GetEmployee', methods=['GET'])
    def employee_account():
        """ Принимает GUID сотрудника и возвращает информацию о балансе сотрудника """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tGetEmployeeAccount\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            # Проверяем наличие Json
            if request.is_json:

                json_request = request.json
                guid = json_request.get('guid')

                if guid:
                    result_db = PCEConnectionDB.take_employee(guid, logger)

                    if result_db['status'] == 'SUCCESS':
                        json_replay['DATA'] = result_db['data']
                        json_replay['RESULT'] = 'SUCCESS'
                    else:
                        json_replay['DESC'] = result_db['desc']

            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tGetEmployeeAccount\tошибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RequestTransaction', methods=['POST'])
    def employee_transaction():
        """ Принимает FGUID сотрудника и возвращает информацию о всех транзакция с его счета """

        if int(OLD_MODE) == 1:  # старый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": ""}

        else:  # новый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tRequestTransaction\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args
            duration = dict()

            duration['data_from'] = res_request.get('data_from')
            duration['data_to'] = res_request.get('data_to')
            guid = res_request.get('guid')

            if guid:
                result_db = TransactionDB.take_employee(guid, duration, logger)

                if result_db['status'] == 'SUCCESS':

                    # старый вариант передачи данных
                    if int(OLD_MODE) == 1:
                        json_replay['RESULT'] = 'SUCCESS'
                        json_replay['DATA'] = result_db['data']

                    else:
                        # Новый вариант
                        json_replay['DATA'] = result_db['data']
                        json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tRequestTransaction\tошибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RequestDecrease', methods=['POST'])
    def employee_decrease():
        """ Принимает FGUID сотрудника и возвращает информацию о всех списаниях с его счета """

        if int(OLD_MODE) == 1:  # старый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": ""}

        else:  # новый вариант передачи данных
            json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tRequestDecrease\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args
            duration = dict()

            duration['data_from'] = res_request.get('data_from')
            duration['data_to'] = res_request.get('data_to')
            guid = res_request.get('guid')

            if guid:
                result_db = DecreaseDB.take(guid, duration, logger)

                if result_db['status'] == 'SUCCESS':

                    # старый вариант передачи данных
                    if int(OLD_MODE) == 1:
                        json_replay['RESULT'] = 'SUCCESS'
                        json_replay['DATA'] = result_db['data']

                    else:
                        # Новый вариант
                        json_replay['DATA'] = result_db['data']
                        json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tRequestDecrease\tошибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    # Добавление гос. номера(авто до 3х штук)

    # RUN SERVER FLASK  ------
    app.run(debug=False, host=set_ini["host"], port=int(set_ini["port"]))
