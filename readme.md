<img src="web_rum_img.png" alt="Описание изображения" width="600">

[![Build Status](https://img.shields.io/badge/python-3.9-green)](https://www.python.org/downloads/) ![Build Status](https://img.shields.io/badge/Flask-2.0.3-red) ![Build Status](https://img.shields.io/badge/PyMySQL-1.1.1-orange)


STEP_1
COMPANY
RequestCompany - Получить информацию о компании
RequestCompanyTransaction - Получить информацию о транзакциях компании за период
RequestEmployees - Получить список сотрудников компании

EMPLOYEE
GetEmployeeInfo - получение информации по сотруднику
-service functions:
    AddAccount - Добавить п.е. сотруднику.                 (не использовать)
    RemoveAccount - Списать в счет компании из сотрудника. (не использовать)

RequestCarsEmployee - Получить список машин сотрудника
RequestDecrease - Получить информацию о списаниях у сотрудника за период
RequestTransaction - Получить информацию о транзакция сотрудника
SetCarEmployee - Добавить номер автомобиля сотруднику
RemoveCarEmployee - Удалить номер автомобиля у сотрудника
SetContacts - Добавить номер телефона и\или почту
SetFavorite - Добавить или убрать сотрудника в избранные

STEP_2
DoRequestCreateCardHolder - Создает заявку в БД на выпуск постоянного пропуска сотруднику
GetRequestCreateCardHolder - Получить список заявок на создание пропуска сотруднику
DoRequestBlockCardHolder - Запрос на удаление (блокировку) владельца карты
DoRequestReplaceCard - Запрос на перевыпуск карты сотрудника (FApacsID)

GetPhoto - получить фотографию по имени файла (не использовать)

STEP_3
DoCreateGuest - Создать заявку в БД для пропуска гостю
GetGuestStatus - Получить статус пропуска гостя на компанию
GetGuestsList - Получить список активных пропусков для гостей на компанию
DoBlockGuest - Заблокировать пропуск гостя
-service functions:
    DoChangeStatus - Изменить статус гостя.                 (не использовать)
    DoTestCarNumber - Протестировать номер автомобиля.      (не использовать)
