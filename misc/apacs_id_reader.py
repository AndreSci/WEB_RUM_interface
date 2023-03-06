
class ApacsClass:

    @staticmethod
    def convect_from_uid(uid: int) -> str:

        ret_value = {"RESULT": "ERROR", "DESC": '', "DATA": dict()}

        try:
            fid = (uid & 0xff_ff_ff_ff_00_00_00_00) >> 32
            f_apacs_id = uid & 0x00_00_00_00_ff_ff_ff_ff

            ret_value['RESULT'] = "SUCCESS"
            ret_value['DATA'] = {'fid': fid, 'f_apacs_id': f_apacs_id}

        except Exception as ex:
            ret_value['DESC'] = f"Ошибка: {ex}"
            print(f"EXEPTION\tApacsClass.convect_from_uid\tИсключение вызвало при работе с {ex}")

        return ret_value
