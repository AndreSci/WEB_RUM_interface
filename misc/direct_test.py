import os


class TestDir:
    """ Класс проверяет наличие папки для сохранения фото """
    def __init__(self, setting_ini: dict):

        self.path_photo = setting_ini.get('photo_path')

    def is_exist(self) -> bool:
        ret_value = False

        if os.path.exists(self.path_photo):
            ret_value = True

        else:
            fail_col = '\033[91m'   # красный текст в консоли

            print(f"{fail_col}ОШИБКА: "
                  f"Не удалось найти путь для сохранения фото указанный в файле settings.ini: {self.path_photo}\n"
                  f"Создайте папку вручную!")

        return ret_value
