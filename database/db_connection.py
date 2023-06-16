import configparser
import os
import threading

import pymysql
import pymysql.cursors

from misc.logger import Logger

LOCK_TH_INI = threading.Lock()


def take_db_settings(db_name: str, logger: Logger):
    """ Функция загружает данные из settings.ini """
    conn_inf = dict()

    settings_file = configparser.ConfigParser()

    if os.path.isfile("./settings.ini"):
        try:
            with LOCK_TH_INI:  # Блокируем потоки
                settings_file.read("settings.ini", encoding="utf-8")

            conn_inf['host'] = str(settings_file[db_name]["HOST"])
            conn_inf['user'] = str(settings_file[db_name]["USER"])
            conn_inf['password'] = str(settings_file[db_name]["PASSWORD"])
            conn_inf['charset'] = str(settings_file[db_name]["CHARSET"])

        except Exception as ex:
            logger.add_log(f"ERROR\ttake_db_settings\tОшибка чтения из settings.ini: {ex}")
            conn_inf = dict()
    else:
        logger.add_log(f"ERROR\ttake_db_settings\tФайл settings.ini не найден в корне API")

    return conn_inf


# Для любой БД из основного раздела в settings.ini
def connect_db(logger: Logger):
    conn_inf = take_db_settings("DATABASE", logger)

    pool = pymysql.connect(host=conn_inf['host'],
                                  user=conn_inf['user'],
                                  password=conn_inf['password'],
                                  charset=conn_inf['charset'],
                                  cursorclass=pymysql.cursors.DictCursor)
    return pool


# Переходная для связи с Румянцево БД
def connect_db_rum(logger: Logger):
    conn_inf = take_db_settings("DATABASE_RUM", logger)

    pool = pymysql.connect(host=conn_inf['host'],
                                  user=conn_inf['user'],
                                  password=conn_inf['password'],
                                  charset=conn_inf['charset'],
                                  cursorclass=pymysql.cursors.DictCursor)
    return pool
