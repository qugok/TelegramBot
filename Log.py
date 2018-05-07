import time


class Log:
    def __init__(self):
        self.__file = 'log/logfile-' + str(
            time.strftime("%d-%m-%Y-%H.%M.%S")) + '.txt'
        with open(self.__file, 'x', encoding='utf-8'):
            pass
        self.write("started")

    def write(self, info: str):
        print("\nstart open")
        with open(self.__file, 'a', encoding='utf-8') as file:
            print("start log")
            file.write(info + '\n')
            print("end log")
