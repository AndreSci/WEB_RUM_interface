import configparser
import os
import threading
import time

from misc.logger import Logger


class AllowedIP:
    """ Класс configparser работает с str """

    def __init__(self):
        self.allow_ip = dict()
        self.TH_LOCK = threading.Lock()
        self.file = configparser.ConfigParser()
        self.file_name = "allowed_ip.ini"

        self.last_m_time = None

    def __read_file(self, logger: Logger) -> bool:
        """ Функция проверяет время последней модификации файла """
        try:
            current_m_time = os.path.getmtime(self.file_name)
        except Exception as ex:
            logger.add_log(f"EXCEPTION\tAllowedIP.__read_file\tОшибка получения данных файла: {ex}")
            # Возвращаем True для попытки чтения файла
            return True

        if self.last_m_time:
            if current_m_time > self.last_m_time:
                logger.add_log(f"EVENT\tAllowedIP.__read_file\tФайл {self.file_name} был модифицирован: "
                               f"было {time.ctime(self.last_m_time)} = "
                               f"стало {time.ctime(current_m_time)}")
                self.last_m_time = current_m_time
                return True
            else:
                return False
        else:
            logger.add_log(f"EVENT\tAllowedIP.__read_file\tФайл {self.file_name} "
                           f"первый раз читается: {time.ctime(current_m_time)}")
            self.last_m_time = current_m_time
            return True

    def read_file(self, logger: Logger):
        """ Функция загрузки данных IP в словарь класса """

        with self.TH_LOCK:
            if os.path.isfile(self.file_name) and self.__read_file(logger):

                try:
                    # Загружаем данные из динамичного файла allowed_ip.ini
                    self.file.read("allowed_ip.ini", encoding="utf-8")

                    self.allow_ip = dict()  # Обнуляем словарь доступа

                    for key, val in self.file["CONNECTIONS"].items():
                        self.allow_ip[key] = int(val)

                except KeyError as ex:
                    logger.add_log(f"ERROR\tAllowedIP.read_file\tОшибка по ключу словаря - {ex}")
                except Exception as ex:
                    logger.add_log(f"ERROR\tAllowedIP.read_file\tException - {ex}")

    def find_ip(self, user_ip: str, logger: Logger, activity_lvl=1) -> bool:
        """ Функция поиска IP в словаре, если нет, \n
            вызывает функцию класса add_ip """

        ret_value = False

        self.read_file(logger)  # Подгружаем данные из файла

        if user_ip in self.allow_ip:
            if self.allow_ip[user_ip] >= activity_lvl:
                ret_value = True
        else:
            # Если нет IP добавляем его в файл и словарь класса
            self.add_ip(user_ip, logger)

        return ret_value

    def add_ip(self, new_ip: str, logger: Logger, activity=0) -> bool:
        """ Функция добавляет IP пользователя в файл со значением str(0)\n
            или если указан как allow_ip='1' """
        ret_value = False

        self.read_file(logger)  # Подгружаем данные из файла

        with self.TH_LOCK:  # Блокируем потоки

            self.file["CONNECTIONS"][new_ip] = str(activity)
            self.allow_ip[new_ip] = activity  # Обязательно должна быть строка

            if os.path.isfile("allowed_ip.ini"):
                try:
                    with open('allowed_ip.ini', 'w') as configfile:
                        self.file.write(configfile)

                    ret_value = True

                    logger.add_log(f"SUCCESS\tAllowedIP.add_ip\t"
                                   f"IP - {new_ip} добавлен в систему со значением {activity}")
                except Exception as ex:
                    logger.add_log(f"ERROR\tAllowedIP.add_ip\tОшибка открытия или записи в файл - {ex}")

        return ret_value
