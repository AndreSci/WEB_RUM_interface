from misc.utility import SettingsIni
import ctypes
from misc.direct_test import TestDir
from misc.consts import ConstsControlClass


def main():

    # Подгружаем данные из settings.ini
    settings = SettingsIni()
    result = settings.create_settings()

    ConstsControlClass.change_log_path(settings.take_log_path())
    ConstsControlClass.change_photo_path(settings.take_photo_path())
    ConstsControlClass.set_terminal_color(settings.take_term_color())

    # Обновляем константы host и port для flask
    main_host, main_port = settings.take_main_host_port()
    ConstsControlClass.change_main_host_port(main_host, main_port)
    # Обновляем константы для apacs_host и apacs_port для APACS_INTERFACE
    apacs_host, apacs_port = settings.take_apacs_host_port()
    ConstsControlClass.change_apacs_host_port(apacs_host, apacs_port)

    fail_col = '\033[91m'
    # end_c = '\033[0m'

    # Проверка успешности загрузки данных
    if not result["result"]:
        print(f"{fail_col}")
        print(f"Ошибка запуска сервиса - {result['desc']}")
        input()
        raise Exception("Service error")

    path_photo_test = TestDir(settings.take_settings())
    if not path_photo_test.is_exist():
        input()
        raise OSError("Path for photo not found")

    port = settings.settings_ini["port"]

    # Меняем имя терминала
    ctypes.windll.kernel32.SetConsoleTitleW(f"REST RUM_API port: {port}")

    # Для обновления констант в файле misc.consts.py
    from flask_server import web_flask

    # ЗАПУСК СЕРВЕРА ФЛАСК
    web_flask()


if __name__ == '__main__':
    main()
