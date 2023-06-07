
RU_CHAR = ['А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
ENG_CHAR = ['A', 'B', 'E', 'K', 'M', 'H', 'O', 'P', 'C', 'T', 'Y', 'X']

ENG_CHAR_DICT = {'A': 'А', 'B': 'В', 'E': 'Е',
                 'K': 'К', 'M': 'М', 'H': 'Н',
                 'O': 'О', 'P': 'Р', 'C': 'С',
                 'T': 'Т', 'Y': 'У', 'X': 'Х'}

GEN_CHAR = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

# Концовка номера (случай когда оператор вводит определение страны из номера авто)
RUS_CHAR_END = ['RUS', 'РУС']


class CarNumberClass:
    """ Класс контроля гос. номеров транспортных средств """
    @staticmethod
    def fix(car_number: str, cancel_rus=True) -> str:
        """ Проверить и исправить номер автомобиля """

        # Выход если нет номера
        if not car_number:
            return ''

        # Проверяем на тип
        if type(car_number) != str:
            car_number = str(car_number)

        # Убираем пробелы и переводим в верхний регистр
        result = car_number.replace(" ", '')
        result = result.upper()

        result_for = list(result)

        result_list = []

        # Пробегаемся по номеру и сохраняем все допустимые символы
        for it in result_for:
            if it in RU_CHAR:
                result_list.append(it)
            elif it in GEN_CHAR:
                if it in ENG_CHAR:
                    result_list.append(ENG_CHAR_DICT[it])
                else:
                    result_list.append(it)

        # Создаем копию готового номера из List в String
        pre_number = ''.join(result_list)
        ret_value = pre_number

        # Если требуется убираем концовку типа 'RUS'
        if cancel_rus:
            if len(result_list) > 3:
                index_max = len(result_list) - 3

                if pre_number[index_max:] in RUS_CHAR_END:
                    ret_value = pre_number[:index_max]

        return ret_value


if __name__ == "__main__":
    print(CarNumberClass.fix('123123ddd'))
