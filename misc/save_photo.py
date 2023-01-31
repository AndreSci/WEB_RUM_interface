import base64
import os
from misc.logger import Logger


class Photo:

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
