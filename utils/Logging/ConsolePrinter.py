from colorama import init
init()


class ConsolePrinter:

    colors = {
        'GREEN': '\033[1;32;40m',
        'BLUE': '\033[1;34;40m',
        'RED': '\033[1;31;40m',
        'WHITE': '\033[1;37;40m',
        'PURPLE': '\033[1;35;40m',
        'YELLOW': '\033[1;33;40m'
    }

    @classmethod
    def print_colored(cls, text, color='WHITE'):
        print(cls.colors[color] + str(text) + '\033[0m')

    @classmethod
    def print_result(cls, text):
        print(cls.colors['GREEN'] + '[RESULT]' + str(text) + '\033[0m')

    @classmethod
    def print_debug(cls, text):
        print(cls.colors['BLUE'] + '[DEBUG]' + str(text) + '\033[0m')

    @classmethod
    def print_warning(cls, text):
        print(cls.colors['YELLOW'] + '[WARNING]' + str(text) + '\033[0m')

    @classmethod
    def print_error(cls, text):
        print(cls.colors['RED'] + '[ERROR]' + str(text) + '\033[0m')

    @classmethod
    def print_critical(cls, text):
        print(cls.colors['PURPLE'] + '[CRITICAL]' + str(text) + '\033[0m')
