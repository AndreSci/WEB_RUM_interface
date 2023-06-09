""" Этап разработки 3 """
from flask import Blueprint, request, jsonify
from misc.consts import ALLOW_IP, LOGGER, ERROR_ACCESS_IP, ERROR_READ_REQUEST

from database.requests.db_guest import GuestClass
from database.requests.db_dark_list_rum import DarkListClass
from database.requests.db_cardholder import CardHolder

from misc.car_number import CarNumberClass

step3 = Blueprint('step3', __name__)


# STEP - 3
# Управление выдачей разовых пропусков для Гостя
@step3.route('/DoCreateGuest', methods=['GET'])
def do_create_guest():
    """ Создаем заявку на пропуск для Гостя """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tDoCreateGuest\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешён ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        try:
            res_request = request.json

            LOGGER.add_log(f"EVENT\tDoRequestGuest\tДанные из запроса: {res_request}", print_it=False)

            login_user = res_request.get("user_id")
            str_inn = res_request.get("inn")
            car_number = CarNumberClass.fix(res_request.get("car_number"))

            # Проверяем пользователя и ИНН
            card_holder_test = CardHolder.test_user(login_user, str_inn, LOGGER)

            if card_holder_test['status'] == "SUCCESS":

                res_dark_list = DarkListClass.find(car_number, LOGGER)

                status_id = 0
                # 1 - Пропуск заказан
                # 2 - Пропуск заказан, автомобиль в черном списке

                if res_dark_list['RESULT'] == 'WARNING':
                    status_id = 2
                elif res_dark_list['RESULT'] == 'ERROR':
                    LOGGER.add_log(f"ERROR\tDoCreateGuest\t"
                                   f"Не удалось обработать данные: {res_request}")
                    json_replay['DESC'] = "Ошибка на сервере"
                else:
                    status_id = 1

                if status_id != 0:
                    json_replay = GuestClass.request_pass(res_request, status_id, car_number, LOGGER)

            else:
                LOGGER.add_log(
                    f"ERROR\tDoCreateGuest\tПользователь заблокирован или ошибка ИНН "
                    f"(id: {login_user} / inn: {str_inn}) - {card_holder_test}")
                json_replay["DESC"] = f"Пользователь заблокирован или ошибка ИНН: {str_inn}"

        except Exception as ex:
            LOGGER.add_log(f"ERROR\tDoCreateGuest\t"
                           f"Не удалось обработать запрос, ошибка данных: {ex}")
            json_replay['DESC'] = "Ошибка запроса, было вызвано исключение"

    return jsonify(json_replay)


@step3.route('/GetGuestsList', methods=['GET'])
def get_guests_list():
    """ Получить статус гостя """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tGetGuestsList\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешён ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        try:
            res_request = request.json

            LOGGER.add_log(f"EVENT\tGetGuestsList\tДанные из запроса: {res_request}", print_it=False)

            login_user = res_request.get("user_id")
            str_inn = res_request.get("inn")

            # Проверяем пользователя и ИНН
            card_holder_test = CardHolder.test_user(login_user, str_inn, LOGGER)

            if card_holder_test['status'] == "SUCCESS":

                id_user = card_holder_test['data'][0]['ID_User']

                json_replay = GuestClass.get_list(id_user, LOGGER)

            else:
                LOGGER.add_log(
                    f"ERROR\tGetGuestsList\tПользователь заблокирован или ошибка ИНН "
                    f"(id: {login_user} / inn: {str_inn}) - {card_holder_test}")
                json_replay["DESC"] = f"Пользователь заблокирован или ошибка ИНН: {str_inn}"

        except Exception as ex:
            LOGGER.add_log(f"ERROR\tGetGuestsList\t"
                           f"Не удалось обработать запрос, ошибка данных: {ex}")
            json_replay['DESC'] = "Ошибка запроса, было вызвано исключение"

    return jsonify(json_replay)


@step3.route('/GetGuestStatus', methods=['GET'])
def get_guest_status():
    """ Получить статус гостя """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tGetGuestStatus\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешён ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        try:
            res_request = request.json

            LOGGER.add_log(f"EVENT\tGetGuestStatus\tДанные из запроса: {res_request}", print_it=False)

            login_user = res_request.get("user_id")
            str_inn = res_request.get("inn")
            id_request = res_request.get("id_request")

            # Проверяем пользователя и ИНН
            card_holder_test = CardHolder.test_user(login_user, str_inn, LOGGER)

            if card_holder_test['status'] == "SUCCESS":

                id_user = card_holder_test['data'][0]['ID_User']

                json_replay = GuestClass.get_status(id_request, id_user, LOGGER)

            else:
                LOGGER.add_log(
                    f"ERROR\tGetGuestStatus\tПользователь заблокирован или ошибка ИНН "
                    f"(id: {login_user} / inn: {str_inn}) - {card_holder_test}")
                json_replay["DESC"] = f"Пользователь заблокирован или ошибка ИНН: {str_inn}"

        except Exception as ex:
            LOGGER.add_log(f"ERROR\tGetGuestStatus\t"
                           f"Не удалось обработать запрос, ошибка данных: {ex}")
            json_replay['DESC'] = "Ошибка запроса, было вызвано исключение"

    return jsonify(json_replay)


@step3.route('/DoBlockGuest', methods=['GET'])
def do_block_guest():
    """ Заблокировать пропуск гостя """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tDoBlockGuest\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешён ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        try:
            res_request = request.json

            LOGGER.add_log(f"EVENT\tDoBlockGuest\tДанные из запроса: {res_request}", print_it=False)

            login_user = res_request.get("user_id")
            str_inn = res_request.get("inn")
            id_remote = res_request.get('id_remote')

            # Проверяем пользователя и ИНН
            card_holder_test = CardHolder.test_user(login_user, str_inn, LOGGER)

            if card_holder_test['status'] == "SUCCESS":

                json_replay = GuestClass.block_pass(id_remote, LOGGER)

            else:
                LOGGER.add_log(
                    f"ERROR\tDoBlockGuest\tПользователь заблокирован или ошибка ИНН "
                    f"(id: {login_user} / inn: {str_inn}) - {card_holder_test}")
                json_replay["DESC"] = f"Пользователь заблокирован или ошибка ИНН: {str_inn}"

        except Exception as ex:
            LOGGER.add_log(f"ERROR\tDoBlockGuest\t"
                           f"Не удалось обработать запрос, ошибка данных: {ex}")
            json_replay['DESC'] = ERROR_READ_REQUEST

    return jsonify(json_replay)


@step3.route('/DoChangeStatus', methods=['GET'])
def do_change_status():
    """ Заблокировать пропуск гостя """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tDoChangeStatus\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешён ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        try:
            res_request = request.json

            LOGGER.add_log(f"EVENT\tDoChangeStatus\tДанные из запроса: {res_request}", print_it=False)

            login_user = res_request.get("user_id")
            str_inn = res_request.get("inn")
            id_request = res_request.get('id_request')
            id_request_status = res_request.get('id_status')

            # Проверяем пользователя и ИНН
            card_holder_test = CardHolder.test_user(login_user, str_inn, LOGGER)

            if card_holder_test['status'] == "SUCCESS":
                id_user = card_holder_test['data'][0]['ID_User']
                json_replay = GuestClass.change_status(id_request, id_request_status, id_user, LOGGER)

            else:
                LOGGER.add_log(
                    f"ERROR\tDoChangeStatus\tПользователь заблокирован или ошибка ИНН "
                    f"(id: {login_user} / inn: {str_inn}) - {card_holder_test}")
                json_replay["DESC"] = f"Пользователь заблокирован или ошибка ИНН: {str_inn}"

        except Exception as ex:
            LOGGER.add_log(f"ERROR\tDoChangeStatus\t"
                           f"Не удалось обработать запрос, ошибка данных: {ex}")
            json_replay['DESC'] = ERROR_READ_REQUEST

    return jsonify(json_replay)
