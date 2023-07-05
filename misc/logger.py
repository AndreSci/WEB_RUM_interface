import threading
import os
import datetime
from threading import Lock


class BColors:
    """ Класс вариантов цвета для текста в консоли """
    col_header = '\033[95m'
    col_okblue = '\033[94m'
    col_okcyan = '\033[96m'
    col_okgreen = '\033[92m'
    col_warning = '\033[93m'
    col_fail = '\033[91m'
    col_endc = '\033[0m'
    col_bold = '\033[1m'
    col_underline = '\033[4m'


def test_dir(log_path) -> bool:
    ret_value = True

    try:
        if not os.path.exists(log_path):  # Если нет директории log_path пробуем её создать.
            os.makedirs(log_path)
            print(f"{BColors.col_warning}Была создана директория для лог-фалов:{BColors.col_endc} {log_path}")
    except Exception as ex:
        print(f"Ошибка при проверка/создании директории лог файлов: {ex}")
        ret_value = False

    return ret_value


# Создаем паттерн одиночка
class SingletonBaseClass(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(SingletonBaseClass, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(metaclass=SingletonBaseClass):
    """ Класс вывода данных в консоль и запись в файл """
    def __init__(self, log_path: str = './logs/', it_color: bool = False):
        self.log_path = log_path
        self.font_color = it_color
        self.log_guard = threading.Lock()

    def add_log(self, text: str, print_it: bool = True) -> bool:
        """ Обшивает текст датой, табуляцией и переходом на новую строку"""

        log_path = self.log_path
        today = datetime.datetime.today()

        for_file_name = str(today.strftime("%Y-%m-%d"))

        date_time = str(today.strftime("%Y-%m-%d/%H.%M.%S"))
        # Создаем лог
        mess = date_time + "\t" + text + "\n"

        if test_dir(log_path):

            if log_path[-1] == '\\' or log_path[-1] == '/':
                pass  # Захотелось использовать pass
            else:
                log_path = log_path + '/'

            with self.log_guard:  # Защищаем поток

                try:
                    if print_it:
                        if self.font_color:
                            if len(text) > 5 and 'ERROR' == text[:5]:
                                print(f"{BColors.col_fail}{date_time}\t{text}{BColors.col_endc}")
                            elif len(text) > 7 and 'WARNING' == text[:7]:
                                print(f"{BColors.col_warning}{date_time}\t{text}{BColors.col_endc}")
                            else:
                                print(date_time + "\t" + text)
                        else:
                            print(date_time + "\t" + text)

                    # Открываем и записываем логи в файл отчета.
                    with open(f'{log_path}{for_file_name}.log', 'a', encoding='utf-8') as file:
                        file.write(mess)
                except Exception as ex:
                    print(f"EXCEPTION\tLogger.add_log()\tSome problem in logger: {ex}")

                ret_value = True
        else:
            ret_value = False

        return ret_value
