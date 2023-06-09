from flask import Blueprint, request, jsonify
from misc.consts import ALLOW_IP, LOGGER, ERROR_ACCESS_IP, ERROR_READ_REQUEST
from misc.car_number import CarNumberClass

service = Blueprint("service", __name__)


@service.route('/DoTestCarNumber', methods=['GET'])
def do_test_car_number():
    """ Проверить гос. номер автомобиля """

    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tDoTestCarNumber\tзапрос от ip: {user_ip}", print_it=False)

    # Проверяем разрешён ли доступ для IP
    if not ALLOW_IP.find_ip(user_ip, LOGGER):
        json_replay["DESC"] = ERROR_ACCESS_IP
    else:

        try:
            res_request = request.json

            LOGGER.add_log(f"EVENT\tDoTestCarNumber\tДанные из запроса: {res_request}", print_it=False)

            json_replay['DATA'] = CarNumberClass.fix(res_request['car_number'])
            json_replay['RESULT'] = "SUCCESS"

        except Exception as ex:
            LOGGER.add_log(f"ERROR\tDoChangeStatus\t"
                           f"Не удалось обработать запрос, ошибка данных: {ex}")
            json_replay['DESC'] = ERROR_READ_REQUEST

    return jsonify(json_replay)


# IP FUNCTION
@service.route('/DoAddIp', methods=['POST'])
def add_ip():
    json_replay = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

    user_ip = request.remote_addr
    LOGGER.add_log(f"EVENT\tDoAddIp\tзапрос от ip: {user_ip}")

    if not ALLOW_IP.find_ip(user_ip, LOGGER, 2):  # Устанавливаем activity_lvl=2 для проверки уровня доступа
        json_replay["DESC"] = "Ошибка доступа по IP"
    else:

        if request.is_json:
            json_request = request.json

            new_ip = json_request.get("ip")
            activity = int(json_request.get("activity"))

            ALLOW_IP.add_ip(new_ip, LOGGER, activity)

            json_replay["RESULT"] = "SUCCESS"
            json_replay["DESC"] = f"IP - {new_ip} добавлен с доступом {activity}"
        else:
            LOGGER.add_log(f"ERROR\tDoCreateGuest\tНе удалось прочитать Json из request")
            json_replay["DESC"] = "Ошибка. Не удалось прочитать Json из request."

    return jsonify(json_replay)
