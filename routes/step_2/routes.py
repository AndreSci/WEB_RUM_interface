""" Этап разработки 2 """
from flask import Blueprint, request, jsonify
from misc.consts import ALLOW_IP, LOGGER, ERROR_ACCESS_IP, ERROR_READ_REQUEST, PHOTO_PATH, APACS_PORT, APACS_HOST

import datetime
import requests
from misc.photo_requests import PhotoClass
from database.requests.db_employee import EmployeeDB
from database.requests.db_cardholder import CardHolder

step2 = Blueprint('step2', __name__)


# STEP 2

# СОЗДАНИЕ ЗАЯВОК НА ПОСТОЯННЫЕ ПРОПУСКА
@step2.route('/DoRequestCreateCardHolder', methods=['GET'])
def create_request_card_holder():
    """ Принимает данные сотрудника и фото. """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tDoRequestCreateCardHolder\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешён ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        json_bool = False

        try:
            res_request = request.json
            img64_size = 0

            if 'img64' in res_request:
                img64_size = len(res_request['img64'])

            # Лог всех входных данных запроса
            LOGGER.add_log(f"EVENT\tDoRequestCreateCardHolder\tДанные из request JSON: "
                           f"user_id: {res_request['user_id']} - "
                           f"inn: {res_request['user_id']} - "
                           f"FLastName: {res_request['user_id']} - "
                           f"FFirstName: {res_request['user_id']} - "
                           f"FPhone: {res_request.get('user_id')} - "
                           f"FMiddleName: {res_request.get('user_id')} - "
                           f"FCarNumber: {res_request.get('user_id')} - "
                           f"FEmail: {res_request.get('user_id')} - "
                           f"img64.size: {img64_size}", print_it=False)

            json_bool = True

        except Exception as ex:
            LOGGER.add_log(f"ERROR\tDoRequestCreateCardHolder\t"
                           f"Не удалось получать данные из запроса, ошибка JSON данных: {ex}")
            res_request = dict()

        if json_bool:
            LOGGER.add_log(f"EVENT\tDoRequestCreateCardHolder\tДанные из request: {res_request.get('inn')}",
                           print_it=False)

            login_user = res_request.get("user_id")
            str_inn = res_request.get("inn")

            # Проверяем пользователя и ИНН
            card_holder_test = CardHolder.test_user(login_user, str_inn, LOGGER)

            if card_holder_test['status'] == "SUCCESS":
                # Проверяем и сохраняем фото

                # Создаем уникальное имя фото
                photo_name = datetime.datetime.today().strftime("%Y%m%d%H%M%S%f")
                photo_name = f"{login_user}_{photo_name}"
                photo_folder = PHOTO_PATH  # + f"\\{login_user}\\"  # Если нужны папки для фото

                # сохраняем фото в файл
                # Photo.test_dir(photo_address, logger)  # Если нужны папки для фото
                res_photo = PhotoClass.save_photo(res_request['img64'], photo_name, photo_folder, LOGGER)

                if res_photo['RESULT'] == 'SUCCESS':
                    # photo_url = photo_folder + photo_name + '.jpg'
                    #
                    # # Получаем полный путь к фото
                    # photo_url = os.path.abspath(photo_url)
                    # photo_url = photo_url.replace('\\', '\\\\')

                    # Создаем заявку в БД
                    # card_holder_create = CardHolder.request_create(res_request, photo_url, logger)
                    card_holder_create = CardHolder.request_create(res_request, (photo_name + '.jpg'), LOGGER)

                    if card_holder_create['status'] == "SUCCESS":
                        json_replay['RESULT'] = "SUCCESS"
                    else:
                        json_replay['DESC'] = card_holder_create['desc']
                else:
                    json_replay['DESC'] = res_photo['DESC']
            else:
                LOGGER.add_log(
                    f"ERROR\tDoRequestCreateCardHolder\tПользователь заблокирован или ошибка ИНН "
                    f"(id: {login_user} / inn: {str_inn})")
                json_replay["DESC"] = f"Пользователь заблокирован или ошибка ИНН: {str_inn}"

        else:
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)


@step2.route('/GetRequestCreateCardHolder', methods=['GET'])
def get_create_request_card_holder():
    """ Принимает user_id и ИНН для поиска заявок. """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tGetRequestCreateCardHolder\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешён ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:
        try:
            res_request = request.json

            login_user = res_request.get("user_id")
            str_inn = res_request.get("inn")

            # Проверяем пользователя и ИНН
            card_holder_test = CardHolder.test_user(login_user, str_inn, LOGGER)

            if card_holder_test['status'] == "SUCCESS":

                # Получаем список заявок на создание пропуска
                list_data = CardHolder.request_list(str_inn, LOGGER)

                if list_data['status'] == 'SUCCESS':
                    json_replay['DATA'] = list_data['data']
                    json_replay['RESULT'] = 'SUCCESS'
                else:
                    json_replay['DESC'] = list_data['desc']

            else:
                LOGGER.add_log(
                    f"ERROR\tGetRequestCreateCardHolder\tПользователь заблокирован или ошибка ИНН "
                    f"(id: {login_user} / inn: {str_inn})")
                json_replay["DESC"] = f"Пользователь заблокирован или ошибка ИНН: {str_inn}"

        except Exception as ex:
            LOGGER.add_log(f"ERROR\tGetRequestCreateCardHolder\t"
                           f"Не удалось получать данные из запроса, ошибка JSON данных: {ex}")
            json_replay["DESC"] = ERROR_READ_REQUEST

    return jsonify(json_replay)


# ОТМЕНА ЗАЯВКИ И ПЕРЕ ВЫПУСК ПРОПУСКА
@step2.route('/DoRequestReplaceCard', methods=['GET'])
def do_request_replace_card():
    """ Создает заявку на перевыпуск карты сотрудника """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tDoRequestReplaceCard\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешён ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        try:
            res_request = request.json

            login_user = res_request.get("user_id")
            str_inn = res_request.get("inn")

            # Проверяем пользователя и ИНН
            card_holder_test = CardHolder.test_user(login_user, str_inn, LOGGER)

            if card_holder_test['status'] == "SUCCESS":

                result_db = CardHolder.recreate_request(res_request, LOGGER)

                if result_db['status'] == 'SUCCESS':
                    json_replay['RESULT'] = 'SUCCESS'
                else:
                    json_replay['DESC'] = result_db['desc']

            else:
                LOGGER.add_log(f"ERROR\tDoRequestReplaceCard\tПользователь заблокирован или ошибка ИНН "
                               f"(id: {login_user} / inn: {str_inn})")
                json_replay["DESC"] = f"Пользователь заблокирован или ошибка ИНН: {str_inn}"

        except Exception as ex:
            LOGGER.add_log(f"ERROR\tDoRequestReplaceCard\t"
                           f"Не удалось получать данные из запроса, ошибка JSON данных: {ex}")

    return jsonify(json_replay)


# БЛОКИРОВКА КАРТЫ И ТАК ЖЕ ОТПРАВЛЯЕТСЯ ЗАПРОС В APACS_INTERFACE НА ЕГО БЛОКИРОВКУ
@step2.route('/DoRequestBlockCardHolder', methods=['GET'])
def do_block_card_holder():
    """ Удаляет заявку на создание пропуска если FStatusID = 1 \n
    принимает user_id, inn и fid заявки """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tDoRequestBlockCardHolder\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешён ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        try:
            res_request = request.json

            LOGGER.add_log(f"EVENT\tDoRequestBlockCardHolder\tДанные из запроса: {res_request}", print_it=False)

            f_apacs_id = res_request.get('FApacsID')
            login_user = res_request.get("user_id")
            str_inn = res_request.get("inn")
            desc = res_request.get('desc')

            if len(desc) > 226:
                json_replay['DESC'] = "Описание причины блокировки не может быть пустым или длиннее 227 символов"
                return jsonify(json_replay)

            info = "Блокировка из личного кабинета"

            # Проверяем пользователя и ИНН
            card_holder_test = CardHolder.test_user(login_user, str_inn, LOGGER)

            if card_holder_test['status'] == "SUCCESS":

                # Проверяем ApacsID на связь с компанией
                in_company = CardHolder.block_card_holder(login_user, str_inn, f_apacs_id, LOGGER)

                if in_company['status'] == 'SUCCESS':
                    # Отправляем запрос в ApacsID на блокировку пользователя
                    url = f"http://{APACS_HOST}:{APACS_PORT}/BlockingCardHolder" \
                          f"?ApacsID={f_apacs_id}&Info={info}&Desc={desc}"

                    res_apacs = requests.get(url, timeout=15).json()

                    if res_apacs.get('RESULT'):
                        json_replay = res_apacs
                    else:
                        json_replay['DESC'] = 'Не удалось заблокировать пользователя'
                        LOGGER.add_log(f"ERROR\tDoRequestBlockCardHolder\t"
                                       f"Не удалось получить данные от Apacs_interface")

                else:
                    json_replay['DESC'] = in_company['desc']

            else:
                LOGGER.add_log(
                    f"ERROR\tDoRequestBlockCardHolder\tПользователь заблокирован или ошибка ИНН "
                    f"(id: {login_user} / inn: {str_inn})")
                json_replay["DESC"] = f"Пользователь заблокирован или ошибка ИНН: {str_inn}"

        except Exception as ex:
            LOGGER.add_log(f"ERROR\tDoRequestBlockCardHolder\t"
                           f"Не удалось обработать запрос, ошибка данных: {ex}")
            json_replay['DESC'] = "Ошибка запроса, было вызвано исключение"

    return jsonify(json_replay)


# РАБОТА С ФОТО

@step2.route('/GetPhoto', methods=['GET'])
def get_photo():
    """ Принимает имя фото"""

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tGetPhoto\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешен ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:
        # получаем данные из параметров запроса
        res_request = request.args

        photo_name = res_request.get('photo_name')

        # Выгружаем фото в base64
        json_replay = PhotoClass.take(photo_name, PHOTO_PATH, LOGGER)

    return jsonify(json_replay)
