import requests
import datetime

import unittest

from tests.json_test import *


def timer_function(function):

    def wrapped(*args):
        start_time = datetime.datetime.now()
        res = function(*args)

        end_time = datetime.datetime.now()
        delta_time = end_time - start_time
        print(f"Скорость работы функции {function.__name__}: {delta_time.total_seconds()} секунд.")
        return res

    return wrapped


class TestRequestRum(unittest.TestCase):

    def test_request_employees(self):
        """ Получаем список сотрудников по GUID компании """

        ret_value = {"RESULT": True, "DESC": '', 'DATA': None}

        guid = "{A25F685A-AC40-4946-B21A-AC1C5B54C705}"
        url = f"http://127.0.0.1:8077/RequestEmployees?GUIDCompany={guid}"

        try:
            result = requests.get(url, timeout=5)

            if result.status_code == 200:
                ret_value['DATA'] = result.json()
            else:
                ret_value['RESULT'] = False
                ret_value['DESC'] = f"Статус код: {result.status_code}"

        except Exception as ex:
            ret_value['RESULT'] = False
            ret_value['DESC'] = ex

        self.assertTrue(ret_value['RESULT'], ret_value)

    def test_add_account(self):
        """ Переместить п.е. от компании к сотруднику """

        ret_value = {"RESULT": True, "DESC": '', 'DATA': None}

        guid = "{B91F3FDF-B8AF-42AE-98D8-29FDD484E245}"
        url = f"http://127.0.0.1:8077/AddAccount?guid={guid}&units=1"

        try:
            result = requests.get(url, timeout=5)

            if result.status_code == 200:

                ret_value['DATA'] = result.json()

                if ret_value['DATA'].get('RESULT') != 'SUCCESS':
                    ret_value['RESULT'] = False
            else:
                ret_value['RESULT'] = False
                ret_value['DESC'] = f"Статус код: {result.status_code}"

        except Exception as ex:
            ret_value['RESULT'] = False
            ret_value['DESC'] = ex

        self.assertTrue(ret_value['RESULT'], ret_value)

    def test_remove_account(self):
        """ Переместить п.е. от сотрудника к компании """

        ret_value = {"RESULT": True, "DESC": '', 'DATA': None}

        guid = "{B91F3FDF-B8AF-42AE-98D8-29FDD484E245}"
        url = f"http://127.0.0.1:8077/RemoveAccount?guid={guid}&units=1"

        try:
            result = requests.get(url, timeout=5)

            if result.status_code == 200:

                ret_value['DATA'] = result.json()

                if ret_value['DATA'].get('RESULT') != 'SUCCESS':
                    ret_value['RESULT'] = False
            else:
                ret_value['RESULT'] = False
                ret_value['DESC'] = f"Статус код: {result.status_code}"

        except Exception as ex:
            ret_value['RESULT'] = False
            ret_value['DESC'] = ex

        self.assertTrue(ret_value['RESULT'], ret_value)

    def test_do_request_create_card_holder(self):
        """ Создает сотрудника """

        ret_value = {"RESULT": True, "DESC": '', 'DATA': None}

        url = f"http://127.0.0.1:8077/DoRequestCreateCardHolder"

        try:
            result = requests.get(url, json=REQ_CREATE_Card_Holder, timeout=5)

            if result.status_code == 200:

                ret_value['DATA'] = result.json()

                if ret_value['DATA'].get('RESULT') != 'SUCCESS':
                    ret_value['RESULT'] = False
            else:
                ret_value['RESULT'] = False
                ret_value['DESC'] = f"Статус код: {result.status_code}"

        except Exception as ex:
            ret_value['RESULT'] = False
            ret_value['DESC'] = ex

        self.assertTrue(ret_value['RESULT'], ret_value)

    def test_set_contacts(self):
        """ Переместить п.е. от сотрудника к компании """

        ret_value = {"RESULT": True, "DESC": '', 'DATA': None}

        guid = "{A37AE0B0-97E7-4084-BFD3-2F312A8EE6CA}"
        phone = 'some_phone2'
        email = 'test@test.org2'
        url = f"http://127.0.0.1:8077/SetContacts?guid={guid}&phone={phone}&email={email}"

        try:
            result = requests.get(url, timeout=5)

            if result.status_code == 200:

                ret_value['DATA'] = result.json()

                if ret_value['DATA'].get('RESULT') != 'SUCCESS':
                    ret_value['RESULT'] = False
            else:
                ret_value['RESULT'] = False
                ret_value['DESC'] = f"Статус код: {result.status_code}"

        except Exception as ex:
            ret_value['RESULT'] = False
            ret_value['DESC'] = ex

        self.assertTrue(ret_value['RESULT'], ret_value)

    def test_get_photo(self):
        """ Получить фотографию """

        ret_value = {"RESULT": True, "DESC": '', 'DATA': None}

        photo_name = '7528_20230131113227779388.jpg'

        url = f"http://127.0.0.1:8077/GetPhoto?photo_name={photo_name}"

        try:
            result = requests.get(url, timeout=5)

            if result.status_code == 200:

                ret_value['DATA'] = result.json()

                if ret_value['DATA'].get('RESULT') != 'SUCCESS':
                    ret_value['RESULT'] = False
            else:
                ret_value['RESULT'] = False
                ret_value['DESC'] = f"Статус код: {result.status_code}"

        except Exception as ex:
            ret_value['RESULT'] = False
            ret_value['DESC'] = ex

        self.assertTrue(ret_value['RESULT'], ret_value)

    def test_set_car_employee(self):
        """ Добавить номер автомобиля сотруднику, Номер может быть записан только на одного сотрудника """

        ret_value = {"RESULT": True, "DESC": '', 'DATA': None}

        guid = '{A37AE0B0-97E7-4084-BFD3-2F312A8EE6CA}'
        car_number = 'у - 197 хе 777'

        url = f"http://127.0.0.1:8077/SetCarEmployee?guid={guid}&car_number={car_number}"

        try:
            result = requests.get(url, timeout=5)

            if result.status_code == 200:

                ret_value['DATA'] = result.json()

                if ret_value['DATA'].get('RESULT') != 'SUCCESS':
                    ret_value['RESULT'] = False
            else:
                ret_value['RESULT'] = False
                ret_value['DESC'] = f"Статус код: {result.status_code}"

        except Exception as ex:
            ret_value['RESULT'] = False
            ret_value['DESC'] = ex

        self.assertTrue(ret_value['RESULT'], ret_value)

    def test_remove_car_employee(self):
        """ Получить фотографию """

        ret_value = {"RESULT": True, "DESC": '', 'DATA': None}

        guid = '{A37AE0B0-97E7-4084-BFD3-2F312A8EE6CA}'
        id_number = 5

        url = f"http://127.0.0.1:8077/RemoveCarEmployee?guid={guid}&fplateid={id_number}"

        try:
            result = requests.get(url, timeout=5)

            if result.status_code == 200:

                ret_value['DATA'] = result.json()

                if ret_value['DATA'].get('RESULT') != 'SUCCESS':
                    ret_value['RESULT'] = False
            else:
                ret_value['RESULT'] = False
                ret_value['DESC'] = f"Статус код: {result.status_code}"

        except Exception as ex:
            ret_value['RESULT'] = False
            ret_value['DESC'] = ex

        self.assertTrue(ret_value['RESULT'], ret_value)


if __name__ == '__main__':
    unittest.main()
