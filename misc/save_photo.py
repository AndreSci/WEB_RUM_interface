import base64
from misc.logger import Logger


class Photo:

    @staticmethod
    def save_photo(file, name: str, photo_address: str, logger: Logger) -> dict:
        ret_value = {"RESULT": "ERROR", "DESC": "", "DATA": ""}

        # TODO Создать рекурсию для контроля папки сохранения фото

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
