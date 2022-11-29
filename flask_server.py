from flask import Flask, render_template, request, make_response, jsonify
import requests
import time

from misc.utility import SettingsIni
from misc.logger import Logger
from misc.allow_ip import AllowedIP, ip_control

from database.requests.db_pce import PCEConnectionDB
from database.requests.db_transaction import TransactionDB
from database.requests.db_decrease import DecreaseDB


ERROR_ACCESS_IP = 'access_block_ip'
ERROR_READ_JSON = 'error_read_request'
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

    # IP FUNCTION -----

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

    # MAIN FUNCTION ------

    # История пополнения и списания парк. ед.
    # Отправлять информацию корпоративный и персональный баланс отдельно

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
                json_replay["DESC"] = ERROR_READ_JSON

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
                json_replay["DESC"] = ERROR_READ_JSON

        return jsonify(json_replay)

    @app.route('/GetEmployee', methods=['GET'])
    def employee_account():
        """ Принимает FApacsID сотрудника и возвращает информацию о балансе сотрудника """

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
                fapacsid = json_request.get('FAID')

                if fapacsid:
                    result_db = PCEConnectionDB.take_employee(fapacsid, logger)

                    if result_db['status'] == 'SUCCESS':
                        json_replay['DATA'] = result_db['data']
                        json_replay['RESULT'] = 'SUCCESS'
                    else:
                        json_replay['DESC'] = result_db['desc']

            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tGetEmployeeAccount\tошибка чтения Json: В запросе нет Json")
                json_replay["DESC"] = ERROR_READ_JSON

        return jsonify(json_replay)

    @app.route('/RequestTransaction', methods=['POST'])
    def employee_transaction():
        """ Принимает temployee.fid сотрудника и возвращает информацию о всех транзакция с его счета """

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
            fid = res_request.get('fid')

            if fid:
                result_db = TransactionDB.take(fid, duration, logger)

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
                json_replay["DESC"] = ERROR_READ_JSON

        return jsonify(json_replay)

    @app.route('/RequestDecrease', methods=['POST'])
    def employee_decrease():
        """ Принимает FEmployeeID сотрудника и возвращает информацию о всех списаниях с его счета """

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
            fid = res_request.get('fid')

            if fid:
                result_db = DecreaseDB.take(fid, duration, logger)

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
                json_replay["DESC"] = ERROR_READ_JSON

        return jsonify(json_replay)

    @app.route('/AddAccount', methods=['POST'])
    def employee_add_account():
        """ Принимает FApacsID сотрудника и кол-во п.е., возвращает информацию об изменениях счета """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tAddAccount\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            json_request = request.json
            fapacsid = json_request.get('FAID')
            units = json_request.get('UNITS')

            if fapacsid and type(units) == int:
                result_db = PCEConnectionDB.add_point(fapacsid, units, logger)

                if result_db['status'] == 'SUCCESS':
                    json_replay['DATA'] = result_db
                    json_replay['RESULT'] = 'SUCCESS'
                else:
                    json_replay['DESC'] = result_db['desc']

            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tAddAccount\tошибка чтения Json: В запросе нет Json")
                json_replay["DESC"] = ERROR_READ_JSON

        return jsonify(json_replay)

    @app.route('/RemoveAccount', methods=['POST'])
    def employee_remove_account():
        """ Принимает FApacsID сотрудника и кол-во п.е., возвращает информацию об изменениях счета """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tRemoveAccount\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            json_request = request.json
            fapacsid = json_request.get('FAID')
            units = json_request.get('UNITS')

            if fapacsid and type(units) == int:
                result_db = PCEConnectionDB.add_point(fapacsid, units, logger)

                if result_db['status'] == 'SUCCESS':
                    json_replay['DATA'] = result_db
                    json_replay['RESULT'] = 'SUCCESS'
                else:
                    json_replay['DESC'] = result_db['desc']

            else:
                # Если в запросе нет Json данных
                logger.add_log(f"ERROR\tRemoveAccount\tошибка чтения Json: В запросе нет Json")
                json_replay["DESC"] = ERROR_READ_JSON

        return jsonify(json_replay)

    # Добавление гос. номера(авто до 3х штук), телефон и почта
    # Удаление и редактирование

    # RUN SERVER FLASK  ------
    app.run(debug=False, host=set_ini["host"], port=int(set_ini["port"]))
