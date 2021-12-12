# скрипт для поиска введенного айпи на оборудовании в выводе команды "show ip interface brief"
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import AuthenticationException
from tabulate import tabulate
from datetime import datetime
import getpass
from os import path
import re

device_types = {'mikrotik_routeros': '1', 'cisco_ios': '2', 'hp_procurve': '3'}

# Функция для подключения к оборудованию по ssh:
def connection(selected_device, host, username, password):

    device = {
        'device_type': selected_device,
        'host': host,
        'username': username,
        'password': password,
        'port': '22',
        'global_cmd_verify': False,
    }
    # Проверка на ошибки при вводе данных:
    try:
        connect_to_device = ConnectHandler(**device)
        return connect_to_device
    except NetMikoTimeoutException: # Проверка на ошибку неправильно введенного ip
        return 'FalseIP'
    except AuthenticationException: # Проверка на ошибку неправильно введенного логина или пароля
        return 'FalseLogPass'


# Функция для нахождения и возврата типа оборудования(ключа) согласно выбранному номеру(значению). Например, ввели номер 1, значит будет возвращено значение "mikrotik_routeros"
def search_device_type(selected_device, device_types):
    selected_device_type = list(device_types.keys())[list(device_types.values()).index(selected_device)]
    return selected_device_type

# Функция для ввода ip:
def input_ip():
    ip = input('Введите ip, который нужно найти: ')
    return ip

# Функция для проверки ip на корректность введенных данных:
def check_ip(ip):
    check = re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip) # Проверяется сколько цифр в октете: должно быть от 1 до 3 цифр
    return check

# Функция для поиска ip в переменной output (в ней записан вывод команды "show ip interface brief"):
def find_ip(ip):
    check_ip(ip)
    find_ip = output.find(str(ip)) # Если find не нашел искомое значение, то он вернет "-1", а если найден - вернет некое положительное число, поэтому просто проверяю на равенство с "-1"
    if find_ip != -1:
        return 'IP адрес найден'
    else:
        return 'IP адрес не найден'

# Функция для записи шапки в файл:
def file_header():
    writing = open('find_ip.csv', 'a')
    writing.write('Дата поиска' + ',' + 'Искомый ip' + ',' + ' Найден ли' + ',' + 'ip оборудования' + ',' + 'Тип оборудования' + '\n')
    writing.close()
    return None

# Функция для записи данных в файл csv (выбрала csv, так как удобно использовать данный формат для последующей работы с полученными данными):
def writing_to_file(ip, result_find_ip, selected_device, host):
    now = datetime.now().strftime("%d-%m-%Y %H:%M") # Для удобства ведения файла записывается время выполнения скрипта
    if path.exists('find_ip.csv') is False: # Данное условие проверяет существование файла и если он не существует, добавляет шапку файла
        file_header()
    else:
        pass
    writing = open('find_ip.csv', 'a')
    writing.write(now + ',' + ip + ',' + result_find_ip + ',' + host + ',' + selected_device + '\n') # запись данных в файл в последовательности согласно шапке
    writing.close()
    return None



# ЛОГИКА СКРИПТА:

# Вывод выбора типа оборудования в виде таблицы (данные для составление таблицы берутся из словаря device_types, который находиться в начале кода)
print(tabulate(device_types.items(), headers=['Тип оборудования', 'Выбрать'], tablefmt="grid"))

# Выбираем тип устройства:
selected_device = search_device_type(input('Выберите устройство (введите значение из второго столбца, соответствующее нужному устройству): '), device_types)

# Производится подключение к оборудованию и выполнение команды "show ip interface brief", также вывод записывается в переменную output:
while True: # цикл нужен чтобы давать возможность ввести данные для подключения заново при повлении ошибки
    # Ввод данных для подключения к оборудованию:
    host = str(input('ip оборудования: '))
    username = str(input('Логин: '))
    password = getpass.getpass('Пароль:')  # в рамках безопасности вводимый пароль не будет отражаться в консоли
    if connection(selected_device, host, username, password)=='FalseIP': # Проверка на ошибку неправильно введенного ip (исходя из возвращенного значения функцией connection())
        print('Введены некорректные данные (ip оборудования)')
    elif connection(selected_device, host, username, password)=='FalseLogPass': # Проверка на ошибку неправильно введенного логина или пароля (исходя из возвращенного значения функцией connection())
        print('Введены некорректные данные (логин или пароль)')
    else: # Если connection() вернул не 'FalseIP' или 'FalseLogPass', то подключение есть и можно отправлять команду:
        output = connection(selected_device, host, username, password).send_command('show ip interface brief')
        # Вывод на экран результата выполнения команды "show ip interface brief":
        print(output)
        break

# Ввод и проверка на корректность ip, который нужно найти в выводе команды "show ip interface brief" (цикл прервется, если функция check_ip() вернет не None:
while True:
    ip = input_ip() # Вводим ip с помощью функции input_ip()
    if check_ip(ip) is None: # check_ip(ip) - проверка на корректность введенного ip
        print('Введен некорректный ip, попробуйте еще раз.')
    else:
        break

# Поиск введенного ip в выводе команды "show ip interface brief":
result_find_ip = find_ip(ip)
# Вывод на экран результата:
print(result_find_ip)

# Запись результата поиска ip в файл (также туда будут записаны искомый ip, найдне он или нет, тип оборудования и его ip):
writing_to_file(ip, result_find_ip, selected_device, host)