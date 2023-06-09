from flask import Flask

from misc.consts import LOGGER, ALLOW_IP, MAIN_HOST, MAIN_PORT

from routes.service.routes import service
from routes.step_1.routes import step1
from routes.step_2.routes import step2
from routes.step_3.routes import step3


ERROR_ACCESS_IP = 'access_block_ip'
ERROR_READ_REQUEST = 'error_read_request'
ERROR_ON_SERVER = 'server_error'


def web_flask():
    """ Главная функция создания сервера Фласк. """

    app = Flask(__name__)  # Объявление сервера

    app.config['JSON_AS_ASCII'] = False

    app.register_blueprint(step1)  # Без Префикса
    app.register_blueprint(step2)  # Без Префикса
    app.register_blueprint(step3)  # Без Префикса
    app.register_blueprint(service)  # Без Префикса

    # Блокируем сообщения фласк
    # block_flask_logs()

    ALLOW_IP.read_file(LOGGER)

    LOGGER.add_log(f"SUCCESS\tweb_flask\tСервер WEB_RUM_Flask начал свою работу")  # log

    # RUN SERVER FLASK  <------
    app.run(debug=False, host=MAIN_HOST, port=MAIN_PORT)
