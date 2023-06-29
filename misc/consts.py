from misc.allow_ip import AllowedIP
from misc.logger import Logger


ERROR_ACCESS_IP = 'access_block_ip'
ERROR_READ_REQUEST = 'error_read_request'
ERROR_ON_SERVER = 'server_error'

ALLOW_IP = AllowedIP()
LOGGER = Logger()

PHOTO_PATH = "C:\\photo\\"

APACS_HOST = ''
APACS_PORT = 0

MAIN_HOST = ''
MAIN_PORT = 0


class ConstsControlClass:
    @staticmethod
    def change_log_path(path: str):
        global LOGGER
        LOGGER.log_path = path

    @staticmethod
    def set_terminal_color(it_color: bool):
        """ Делает терминал цветным если True """
        global LOGGER
        LOGGER.font_color = it_color

    @staticmethod
    def change_photo_path(photo_path: str):
        global PHOTO_PATH
        PHOTO_PATH = photo_path

    @staticmethod
    def change_main_host_port(host, port):
        global MAIN_HOST
        global MAIN_PORT

        MAIN_PORT = int(port)
        MAIN_HOST = str(host)

    @staticmethod
    def change_apacs_host_port(host, port):
        global APACS_HOST
        global APACS_PORT

        APACS_PORT = int(port)
        APACS_HOST = str(host)
