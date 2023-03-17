import os
import configparser


class SettingsIni:

    def __init__(self):
        # general settings
        self.settings_ini = dict()
        self.settings_file = configparser.ConfigParser()

    def create_settings(self) -> dict:
        """ Функция получения настройки из файла settings.ini. """
        error_mess = 'Успешная загрузка данных из settings.ini'
        ret_value = dict()
        ret_value["result"] = False

        # проверяем файл settings.ini
        if os.path.isfile("settings.ini"):
            try:
                self.settings_file.read("settings.ini", encoding="utf-8")
                # general settings ----------------------------------------
                self.settings_ini["host"] = self.settings_file["GENERAL"]["HOST"]
                self.settings_ini["port"] = self.settings_file["GENERAL"]["PORT"]
                self.settings_ini['apacs_host'] = self.settings_file['APACS_INTERFACE']['HOST']
                self.settings_ini['apacs_port'] = self.settings_file['APACS_INTERFACE']['PORT']

                if "LOG_PATH" in self.settings_file["GENERAL"]:
                    self.settings_ini["log_path"] = self.settings_file["GENERAL"]["LOG_PATH"]
                else:
                    self.settings_ini["log_path"] = './logs/'

                if 'PHOTO' in self.settings_file:
                    self.settings_ini["photo_path"] = self.settings_file["PHOTO"]["PATH"]
                else:
                    self.settings_ini["photo_path"] = './photo/'

                ret_value["result"] = True

            except KeyError as ex:
                error_mess = f"Не удалось найти поле в файле settings.ini: {ex}"

            except Exception as ex:
                error_mess = f"Не удалось прочитать файл: {ex}"
        else:
            error_mess = "Файл settings.ini не найден в корне проекта"

        ret_value["desc"] = error_mess

        return ret_value

    def take_settings(self):
        return self.settings_ini

    def take_log_path(self):
        return self.settings_ini["log_path"]
