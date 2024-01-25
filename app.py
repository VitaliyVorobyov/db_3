from settings import settings
from db import Request


class User:

    def __init__(self) -> None:
        self.first_name = input('Введите имя: ')
        self.last_name = input('Введите фамилию: ')
        self.email = input('Введите почту: ')
        self.phone = input('Введите номер телефона: ')
        self.__post_init__()

    def __post_init__(self) -> None:
        if self.first_name == '':
            self.first_name = None
        if self.last_name == '':
            self.last_name = None
        if self.email == '':
            self.email = None
        elif self.phone == '':
            self.phone = None


def run(request: Request) -> None:
    while True:

        request.create_table()
        command = input(
            ' 1 - добавить клиента;\n'
            ' 2 - добавить телефон для существующего клиента;\n'
            ' 3 - изменить данные о клиенте;\n'
            ' 4 - удалить телефон для существующего клиента;\n'
            ' 5 - удалить существующего клиента;\n'
            ' 6 - поиск клиента;\n'
            ' 7 - выход из программы;\n'
            'Введите команду:'
        )

        if command == '1':
            user = User()
            if None in [user.first_name, user.last_name, user.email]:
                print('Поля не могут быть пустыми. Повторите ввод:\n')
                continue
            user_id = request.add_user(user.first_name, user.last_name, user.email)
            if user_id is None:
                print('Такой пользователь уже существует. Повторите ввод:\n')
                continue
            if user.phone is not None:
                request.add_phone(user_id, user.phone)
            print('Пользователь добавлен.\n')
        elif command == '2':
            user_id = int(input('Введите id пользователя: '))
            phone = input('Введите номер телефона: ')
            request.add_phone(user_id, phone)
            print('Номер добавлен.\n')
        elif command == '3':
            user_id = int(input('Введите id пользователя: '))
            user = User()
            request.edit_user(user_id, user.first_name, user.last_name, user.email)
            if user.phone is not None:
                request.delete_phone(user_id)
                request.add_phone(user_id, user.phone)
            print('Данные изменены.\n')
        elif command == '4':
            user_id = int(input('Введите id пользователя: '))
            request.delete_phone(user_id)
            print('Телефон удален.\n')
        elif command == '5':
            user_id = int(input('Введите id пользователя: '))
            request.delete_user(user_id)
            print('Пользователь удален.\n')
        elif command == '6':
            user = User()
            get = request.get_user(user.email, user.phone, user.first_name, user.last_name)
            for el in get:
                print(f'id: {el[0]}, Имя: {el[1]}, Фамилия: {el[2]}, Почта: {el[3]},'
                      f' Номер телефона: {el[4] if el[4] else "не указан"},'
                      f' id телефона: {el[5] if el[5] else "не указан"}')
        elif command == '7':
            print('Программа завершена.')
            break


if __name__ == '__main__':
    run(request=Request(settings.database.username, settings.database.password, settings.database.host,
                        settings.database.port, settings.database.database_name))
