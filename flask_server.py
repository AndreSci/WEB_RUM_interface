from flask import Flask, render_template, request, make_response, jsonify
import datetime

from misc.utility import SettingsIni
from misc.logger import Logger
from misc.allow_ip import AllowedIP
from misc.save_photo import Photo

from database.requests.db_pce import PCEConnectionDB
from database.requests.db_transaction import TransactionDB
from database.requests.db_decrease import DecreaseDB
from database.requests.db_employee import EmployeeDB
from database.requests.db_cardholder import CardHolder


ERROR_ACCESS_IP = 'access_block_ip'
ERROR_READ_REQUEST = 'error_read_request'
ERROR_ON_SERVER = 'server_error'


def web_flask(logger: Logger, settings_ini: SettingsIni):
    """ Главная функция создания сервера Фласк. """

    app = Flask(__name__)  # Объявление сервера

    app.config['JSON_AS_ASCII'] = False

    # Блокируем сообщения фласк
    # block_flask_logs()

    set_ini = settings_ini.take_settings()

    allow_ip = AllowedIP()
    allow_ip.read_file(logger)

    logger.add_log(f"SUCCESS\tweb_flask\tСервер WEB_RUM_Flask начал свою работу")  # log

    # IP FUNCTION

    @app.route('/DoAddIp', methods=['POST'])
    def add_ip():
        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

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

    # - COMPANY

    @app.route('/RequestCompany', methods=['GET'])
    def company_information():
        """ Принимает id и ИНН компании и возвращает информацию о балансе компании """

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

            logger.add_log(f"EVENT\tRequestCompany\tПолучены данные: "
                           f"(InnCompany: {inn_company} IDCompany: {id_company})", print_it=False)

            if inn_company:
                result_db = PCEConnectionDB.take_company(id_company, inn_company, logger)

                if result_db['status'] == 'SUCCESS':

                    json_replay['DATA'] = result_db['data'][0]
                    json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tRequestCompany\tОшибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RequestEmployees', methods=['GET'])
    def employees_list():
        """ Принимает GUID компании и возвращает информацию список сотрудников компании """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tRequestEmployees\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args
            guid_company = res_request.get('GUIDCompany')

            logger.add_log(f"EVENT\tRequestEmployees\tПолучены данные: "
                           f"(GUIDCompany: {guid_company})", print_it=False)

            if guid_company:
                result_db = PCEConnectionDB.find_employees(guid_company, logger)

                if result_db['status'] == 'SUCCESS':

                    json_replay['DATA'] = result_db['data']
                    json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tRequestEmployees\tОшибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RequestCompanyTransaction', methods=['GET'])
    def company_transaction():
        """ Принимает FGUID компании и возвращает информацию о всех транзакция """

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

            logger.add_log(f"EVENT\tRequestTransaction\tПолучены данные: "
                           f"(data_from: {duration['data_from']} data_to: {duration['data_to']} guid: {guid})",
                           print_it=False)

            if guid:
                result_db = TransactionDB.take_company(guid, duration, logger)

                if result_db['status'] == 'SUCCESS':

                    json_replay['DATA'] = result_db['data']
                    json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tRequestCompanyTransaction\tОшибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    # - EMPLOYEE

    # employee car
    @app.route('/SetCarEmployee', methods=['GET'])
    def set_employee_car():
        """ Принимает GUID сотрудника и номер автомобиля который нужно к нему привязать """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tSetCarEmployee\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args

            guid = str(res_request.get('guid'))
            car_number = str(res_request.get('car_number'))

            logger.add_log(f"EVENT\tSetCarEmployee\tПолучены данные: "
                           f"(car_number: {car_number} guid: {guid})",
                           print_it=False)

            # изменяем номер в нужный формат
            car_number = car_number.upper()

            for it in (' ', '/', '.', '-'):
                car_number = car_number.replace(it, '')

            if guid:

                result_db = EmployeeDB.set_car_number(guid, car_number, logger)

                if result_db['status'] == 'SUCCESS':

                    json_replay['DATA'] = result_db['data']
                    json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tSetCarEmployee\tОшибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RemoveCarEmployee', methods=['GET'])
    def remove_employee_car():
        """ Принимает GUID сотрудника и номер авто который нужно удалить """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tRemoveCarEmployee\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args

            guid = str(res_request.get('guid'))
            f_plate_id = str(res_request.get('fplateid'))

            logger.add_log(f"EVENT\tRemoveCarEmployee\tПолучены данные: "
                           f"(fplateid: {f_plate_id} guid: {guid})",
                           print_it=False)

            if guid:

                result_db = EmployeeDB.remove_car_number(guid, f_plate_id, logger)

                if result_db['status'] == 'SUCCESS':

                    json_replay['DATA'] = result_db['data']
                    json_replay['RESULT'] = 'SUCCESS'
                    json_replay['DESC'] = result_db['desc']

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tRemoveCarEmployee\tОшибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RequestCarsEmployee', methods=['GET'])
    def get_employee_cars():
        """ Принимает GUID сотрудника и возвращает номера машин привязанных к нему """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tSetContacts\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args

            guid = res_request.get('guid')

            logger.add_log(f"EVENT\tRequestCarsEmployee\tПолучены данные: "
                           f"(guid: {guid})",
                           print_it=False)

            if guid:

                result_db = EmployeeDB.get_car_numbers(guid, logger)

                if result_db['status'] == 'SUCCESS':

                    json_replay['DATA'] = result_db['data']
                    json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tSetContacts\tОшибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    # employee
    @app.route('/SetContacts', methods=['GET'])
    def employee_contacts():
        """ Принимает GUID сотрудника, номер телефона, email\n
        так же можно указывать один из двух параметров phone/email """

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

            logger.add_log(f"EVENT\tSetContacts\tПолучены данные: "
                           f"(guid: {guid} phone: {phone} email: {email})",
                           print_it=False)

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

                    json_replay['DATA'] = result_db['data']
                    json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tSetContacts\tОшибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/SetFavorite', methods=['GET'])
    def employee_favorite():
        """ Принимает GUID сотрудника и значение is_favorite где может быть 1 или 0 """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tSetFavorite\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args

            guid = res_request.get('guid')

            logger.add_log(f"EVENT\tSetFavorite\tПолучены данные: "
                           f"(guid: {guid})",
                           print_it=False)

            try:
                is_favorite = int(res_request.get('is_favorite'))
            except Exception as ex:
                logger.add_log(f"ERROR\tSetFavorite\tОшибка чтения request: В запросе {ex}")
                is_favorite = 173317

            if guid and 0 <= is_favorite <= 1:

                result_db = EmployeeDB.set_favorite(guid, is_favorite, logger)

                if result_db['status'] == 'SUCCESS':
                    json_replay['RESULT'] = 'SUCCESS'
                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет данных
                if is_favorite != 173317:
                    logger.add_log(f"ERROR\tSetFavorite\tОшибка чтения request: "
                                   f"В запросе guid: {guid} is_favorite: {is_favorite}")
                json_replay["DESC"] = "Ошибка. is_favorite может быть только 1 или 0"

        return jsonify(json_replay)

    @app.route('/AddAccount', methods=['GET'])
    def employee_add_account():
        """ Принимает FGUID сотрудника и кол-во п.е. """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tAddAccount\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args
            guid = res_request.get('guid')
            units = int(res_request.get('units'))

            logger.add_log(f"EVENT\tAddAccount\tПолучены данные: "
                           f"(guid: {guid} units: {units})",
                           print_it=False)

            if guid and units:
                result_db = PCEConnectionDB.add_point(guid, units, logger)

                if result_db['status'] == 'SUCCESS':
                    json_replay['RESULT'] = 'SUCCESS'
                else:
                    json_replay['DESC'] = result_db['desc']

            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tAddAccount\tОшибка чтения request: В запросе нет числа или GUID")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RemoveAccount', methods=['GET'])
    def employee_remove_account():
        """ Принимает FGUID сотрудника и кол-во п.е. """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tRemoveAccount\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args

            guid = res_request.get('guid')
            units = int(res_request.get('units'))

            logger.add_log(f"EVENT\tRemoveAccount\tПолучены данные: "
                           f"(guid: {guid} units: {units})",
                           print_it=False)

            if guid and units:
                result_db = PCEConnectionDB.remove_point(guid, units, logger)

                if result_db['status'] == 'SUCCESS':
                    json_replay['RESULT'] = 'SUCCESS'
                else:
                    json_replay['DESC'] = result_db['desc']

            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tRemoveAccount\tОшибка чтения request: В запросе нет числа или GUID")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RequestTransaction', methods=['GET'])
    def employee_transaction():
        """ Принимает FGUID сотрудника, период и возвращает информацию о всех транзакция с его счета """

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

            logger.add_log(f"EVENT\tRequestTransaction\tПолучены данные: "
                           f"(guid: {guid} data_from: {duration['data_from']} data_to: {duration['data_to']})",
                           print_it=False)

            if guid:
                result_db = TransactionDB.take_employee(guid, duration, logger)

                if result_db['status'] == 'SUCCESS':

                    json_replay['DATA'] = result_db['data']
                    json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tRequestTransaction\tОшибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/RequestDecrease', methods=['GET'])
    def employee_decrease():
        """ Принимает FGUID сотрудника и возвращает информацию о всех списаниях с его счета """

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

            logger.add_log(f"EVENT\tRequestDecrease\tПолучены данные: "
                           f"(guid: {guid} data_from: {duration['data_from']} data_to: {duration['data_to']})",
                           print_it=False)

            if guid:
                result_db = DecreaseDB.take(guid, duration, logger)

                if result_db['status'] == 'SUCCESS':

                    json_replay['DATA'] = result_db['data']
                    json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tRequestDecrease\tОшибка чтения request: В запросе нет данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    @app.route('/SetAutoBalance', methods=['GET'])
    def set_auto_balance():
        """ Принимает FGUID сотрудника и кол-во п.е. для авто пополнения """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tSetAutoBalance\tзапрос от ip: {user_ip}")

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            res_request = request.args

            guid = res_request.get('guid')
            units = int(res_request.get('units'))

            logger.add_log(f"EVENT\tSetAutoBalance\tПолучены данные: "
                           f"(guid: {guid} units: {units})",
                           print_it=False)

            try:
                units = int(units)
            except Exception as ex:
                logger.add_log(f"ERROR\tSetAutoBalance\tНе удалось конвертировать units: {units} - {ex}")
                units = -1

            if guid and units >= 0:
                result_db = EmployeeDB.set_auto_balance(guid, units, logger)

                if result_db['status'] == 'SUCCESS':

                    json_replay['DATA'] = result_db['data']
                    json_replay['RESULT'] = 'SUCCESS'

                else:
                    json_replay['DESC'] = result_db['desc']
            else:
                # Если в запросе нет данных
                logger.add_log(f"ERROR\tSetAutoBalance\tОшибка чтения request: В запросе ошибка данных")
                json_replay["DESC"] = ERROR_READ_REQUEST

        return jsonify(json_replay)

    # СОЗДАНИЕ ЗАЯВОК НА ПОСТОЯННЫЕ ПРОПУСКА

    @app.route('/DoRequestCreateCardHolder', methods=['GET'])
    def create_request_card_holder():
        """ Принимает данные сотрудника и фото. """

        json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        user_ip = request.remote_addr
        logger.add_log(f"EVENT\tDoRequestCreateCardHolder\tзапрос от ip: {user_ip}", print_it=False)

        # Проверяем разрешен ли доступ для IP
        if not allow_ip.find_ip(user_ip, logger):
            json_replay["DESC"] = ERROR_ACCESS_IP
        else:

            try:
                res_request = request.json
            except Exception as ex:
                logger.add_log(f"ERROR\tDoRequestCreateCardHolder\tДанные из request JSON пусты {ex}")
                res_request = dict()

            if len(res_request) > 0:
                logger.add_log(f"EVENT\tDoRequestCreateCardHolder\tДанные из request: {res_request.get('inn')}",
                               print_it=False)

                login_user = res_request.get("user_id")
                str_inn = res_request.get("inn")

                # Проверяем пользователя и ИНН
                card_holder_test = CardHolder.test_user(login_user, str_inn, logger)

                if card_holder_test['status'] == "SUCCESS":
                    # Проверяем и сохраняем фото

                    photo_name = datetime.datetime.today().strftime("%Y%m%d%H%M%S%f")
                    photo_address = set_ini['photo_path']

                    res_photo = Photo.save_photo(res_request['img64'], photo_name, photo_address, logger)

                    if res_photo['RESULT'] == 'SUCCESS':
                        photo_address = photo_address + photo_name + '.jpg'
                        card_holder_create = CardHolder.request_create(res_request, photo_address, logger)

                        if card_holder_create['status'] == "SUCCESS":
                            json_replay['RESULT'] = "SUCCESS"
                        else:
                            json_replay['DESC'] = card_holder_create['desc']
                    else:
                        json_replay['DESC'] = res_photo['DESC']
                else:
                    logger.add_log(
                        f"ERROR\tDoRequestCreateCardHolder\tПользователь заблокирован или ошибка ИНН "
                        f"({login_user} : {str_inn})")
                    json_replay["DESC"] = f"Пользователь заблокирован или ошибка ИНН: {str_inn}"

            else:
                logger.add_log(f"ERROR\tDoRequestCreateCardHolder\tНе удалось получать данные из запроса, JSON пуст.")

        return jsonify(json_replay)

    # RUN SERVER FLASK  ------
    app.run(debug=False, host=set_ini["host"], port=int(set_ini["port"]))
