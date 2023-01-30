from misc.utility import SettingsIni
from misc.logger import Logger
from flask_server import web_flask
import time
import ctypes
from misc.direct_test import TestDir


def main():

    # Подгружаем данные из settings.ini
    settings = SettingsIni()
    result = settings.create_settings()

    # Проверка успешности загрузки данных
    if not result["result"]:
        print(f"Ошибка запуска сервиса - {result['desc']}")
        input()
        return

    path_photo_test = TestDir(settings.take_settings())
    if not path_photo_test.is_exist():
        input()
        return

    port = settings.settings_ini["port"]

    # Меняем имя терминала
    ctypes.windll.kernel32.SetConsoleTitleW(f"REST RUM_API port: {port}")

    # Обьявляем логирование
    logger = Logger(settings)

    # Запуск сервера фласк
    web_flask(logger, settings)


if __name__ == '__main__':
    main()
