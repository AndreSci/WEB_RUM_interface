import base64
import os
from misc.logger import Logger


class PhotoClass:

    @staticmethod
    def test_dir(photo_path: str, logger: Logger) -> bool:
        """ Проверяем на наличие папки в директории для сохранения фото, создаем если её нет"""
        ret_value = True

        try:
            if not os.path.exists(photo_path):  # Если нет директории пробуем её создать.
                os.makedirs(photo_path)
        except Exception as ex:
            logger.add_log(f"ERROR\tPhoto.test_dir\tОшибка, не удалось создать папку для фото: {ex}")
            ret_value = False

        return ret_value

    @staticmethod
    def save_photo(file, name: str, photo_address: str, logger: Logger) -> dict:
        ret_value = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        # Проверяем на формат JPG где в разметке base64 первые символы будут означать /9j/4A
        if file[:6] == '/9j/4A':

            try:
                decoded_data = base64.b64decode(file)

                if photo_address[-1] == '\\' or photo_address[-1] == '/':
                    pass  # Захотелось использовать pass
                else:
                    photo_address = photo_address + '/'

                img_file = open(f'{photo_address}{name}.jpg', 'wb')
                img_file.write(decoded_data)
                img_file.close()

                ret_value['RESULT'] = 'SUCCESS'
            except Exception as ex:
                logger.add_log(f"ERROR\tPhoto.save_photo\tИсключение в попытке Декодировать и записать в файл: {ex}")
                ret_value['DESC'] = 'Не удалось сохранить фото, ошибка на сервере'
        else:
            logger.add_log(f"ERROR\tPhoto.save_photo\tКодировка фото не соответствует JPG: {file[:6]}")
            ret_value['DESC'] = 'Кодировка фото не соответствует JPG'

        return ret_value

    @staticmethod
    def take(url: str, photo_address: str, logger: Logger):

        ret_value = {"RESULT": "ERROR", "DESC": '', "DATA": dict()}

        if photo_address[-1] == '\\' or photo_address[-1] == '/':
            pass  # Захотелось использовать pass
        else:
            photo_address = photo_address + '/'

        if os.path.isfile(f"{photo_address}{url}"):
            try:
                with open(f"{photo_address}{url}", "rb") as file:

                    ret_value['DATA']['img64'] = base64.b64encode(file.read()).decode('utf-8')

                ret_value['RESULT'] = "SUCCESS"

            except Exception as ex:
                logger.add_log(f"ERROR\tPhotoWork.take\tНе удалось получить данных по указанному адресу: {ex}")
                ret_value['DESC'] = ret_value['DESC'] + f"Не удалось прочитать файл: {url}"
        else:
            logger.add_log(f"ERROR\tPhotoWork.take\tНе удалось найти файл: {url}")
            ret_value['DESC'] = ret_value['DESC'] + f"Не удалось найти файл: {url}"

        return ret_value