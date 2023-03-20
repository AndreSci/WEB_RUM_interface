class UserUid:
    """ Класс обработки связанных с UID """

    @staticmethod
    def take(f_apacs_id: int, fid: int) -> int:
        """ Принимает FApacsID и FID """

        # Побитовый сдвиг для получения FUID
        uid = (fid << 32) | f_apacs_id

        return uid
