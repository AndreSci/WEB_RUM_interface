class UserUid:
    """ Класс обработки связанных с UID """

    @staticmethod
    def take(f_apacs_id: int, fid: int) -> int:
        """ Принимает FApacsID и FID и возвращает UID """

        # Побитовый сдвиг для получения FUID
        uid = (fid << 32) | f_apacs_id

        return uid

    @staticmethod
    def reverse_uid(uid: int) -> dict:
        """ Возвращает словарь с полями FApacsID и FID """

        ret_value = dict()

        # Побитовый сдвиг для получения FUID
        # uid = (fid << 32) | f_apacs_id

        ret_value['FApacsID'] = uid & 0xffffffff
        ret_value['FID'] = uid >> 32

        return ret_value


if __name__ == "__main__":

    print(UserUid.take(1055529, 59706))
    print(UserUid.reverse_uid(256435318430505))