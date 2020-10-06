import requests
from bs4 import BeautifulSoup


class Parser():
    '''
    Класс определяющий общие свойства и методы для всех парсеров

    Публичные методы:
    get_data() - возвращает искомые значения.
    Метод вызывается ИЗ ЭКЗЕМПЛЯРОВ ПОТОМКОВ данного класса.
    set_ads(ads_list) - устанавливает в свойство _ads_list объекта список с
    кортежами данных, которые, как ожидается получены путем парсинга других
    сайтов.
    Метод вызывается ИЗ ЭКЗЕМПЛЯРОВ ПОТОМКОВ данного класса.
    '''

    def __init__(self):
        # Заголовки для GET-запроса
        self._header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) ' +
            'Chrome/80.0.3987.116 Safari/537.36'}
        # Адрес текущей страницы
        self._url = None
        # Текущий объект BeautifulSoup
        self._soup = None
        # Результирущий список
        self._ads_list = []

    def _get_page_data(self):
        '''Вытягивает данные со страницы'''

        # Делаем запрос
        page_data = requests.get(self._url, headers=self._header)
        # Конвертируем результат запроса в объект BeautifulSoup
        # и записываем его в соответствующее свойство объекта
        self._soup = BeautifulSoup(page_data.text, 'lxml')

    def _checklist(self, checked_tuple):
        ''' Добавляет или отклоняет запись в результирующий список.
        Уникальность проверяется по двум полям: "employeer" и "title" '''

        # Переменная указывающая на то, нашлось ли совпадение
        check = False
        # Сравниваем проверяемый кортеж с существующими кортежами списка
        for iter_tuple in self._ads_list:
            # Проверка на уникальность по первому полю(заголовок объявления)
            cond_title = checked_tuple[0].lower() == iter_tuple[0].lower()
            # Проверка на уникальность по второму полю(работодатель)
            cond_employeer = checked_tuple[1].lower() == iter_tuple[1].lower()
            # Если совпадение обнаружено по обоим полям
            if cond_title and cond_employeer:
                # Указываем, что совпадение найдено
                check = True
                # Прекращаем просматривать результирующий список
                break
        # Если после просмотра результирующего списка совпадение не найдено
        if not check:
            # Добавляем проверяемый кортеж в результирующий список
            self._ads_list.append(checked_tuple)

    def get_data(self):
        ''' Возвращает список кортежей с искомыми значениями '''

        # Пока значение url действительно (True)
        while self._url:
            # Делаем запрос по текущему URL -> получаем объект BS4 ->
            # -> записываем его в соответствующее свойство объекта
            self._get_page_data()
            # Получаем необходимые данные из объекта BS4 -> фильтруем их ->
            # -> записываем в результирующий список
            self._get_details()
            # Находим ссылку на следющую страницу -> ЕСЛИ таковая имеется =>
            # => записываем её в соответствующее свойство объекта ==> ИНАЧЕ =>
            # => указываем, что ссылки на следющую страницу нет
            self._pagination()

        # Возвращает результирующий список
        return self._ads_list

    def set_ads(self, ads_list):
        '''Устанавливает в свойство, которое определяет результирующий список
        список с кортежами данных (из парсинга других сайтов)'''

        # Устанавливаемый объект должен иметь тип - список
        cond_type = type(ads_list) == list
        # Устанавливаемый список должен состоять из кортежей
        cond_contents = True
        for ad in ads_list:
            if type(ad) != tuple:
                cond_contents = False
                print(f'Элемент {ad} - не является кортежем')
                break
        # Если получаемый объект удовлетворяет условиям -> устанавливаем
        if cond_type and cond_contents:
            self._ads_list = ads_list
        elif not cond_type:
            print(f'Устанавливаемый объект должен иметь тип - список(list) ' +
                  f'а Вы передали {type(ads_list)}')
        elif not cond_contents:
            print('Устанавливаемый список должен состоять из кортежей')

        return self


class HhParser(Parser):
    '''
    Класс определяющий методы для парсера сайта hh.ru

    Имеет единственный публичный метод set_url(), что принимает от
    пользователя начальное значение url-адреса с которого начинается
    работа парсера
    '''

    def set_url(self, url_str):
        # Если передаваемое значение является ссылкой на hh.ru
        if url_str[:13] == 'https://hh.ru':
            # Записываем его в соответствующее свойство объекта
            self._url = url_str

            return self

    def _get_details(self):
        '''Добавляет к списку с объявлениями новые кортежи'''
        # Находит все контейнеры с объявлениями в текущем массиве данных
        ads = self._soup.find('div', class_='vacancy-serp').find_all(
            'div', class_='vacancy-serp-item')
        # Находит интересующие нас данные в каждом контейнере
        for ad in ads:
            # Заголовок объявления
            title = ad.find(
                'span', class_='g-user-content').find('a').text.strip()
            # Ссылка на страницу объявления
            link = ad.find(
                'span', class_='g-user-content').find('a').get('href')
            # Наименование работодателя
            employeer = ad.find(
                'div', class_='vacancy-serp-item__meta-info'
            ).find('a').text.strip()
            # Размер заработной платы
            salary = ad.find(
                'div', class_='vacancy-serp-item__sidebar'
            ).text.replace('\xa0', '')
            if salary == '':
                salary = 'не указана'
            # Запись полученых данных в кортеж
            ad_data = (title, employeer, link, salary)
            # Проверка записи на уникальность и запись в результирующий список
            self._checklist(ad_data)

    def _pagination(self):
        '''Изменяет ссылку на следующую страницу. Изменяет её на False, если
        следующей страницы нет'''
        first_part_link = 'https://hh.ru'
        # Получение ссылки на следующую странцицу
        try:
            self._url = first_part_link + self._soup.find(
                'a', class_='HH-Pager-Controls-Next').get('href')
        # Если таковой нет, то указываем это
        except AttributeError:
            self._url = False


class WorkUaParser(Parser):
    '''
    Класс определяющий методы для парсера сайта work.ua

    Имеет единственный публичный метод set_url(), что принимает от
    пользователя начальное значение url-адреса с которого начинается
    работа парсера
    '''

    def set_url(self, url_str):
        ''' Устанавливает стартовую ссылку для парсинга '''
        # Если передаваемое значение является ссылкой на work.ua
        if url_str[:19] == 'https://www.work.ua':
            # Записываем его в соответствующее свойство объекта
            self._url = url_str

            return self

    def _get_details(self):
        '''Добавляет к списку с объявлениями новые кортежи'''
        # Находит все контейнеры с объявлениями в текущем массиве данных
        ads = self._soup.find_all('div', class_='card-hover')
        # Находит интересующие нас данные в каждом контейнере
        for ad in ads:
            # Заголовок объявления
            title = ad.find('a').text
            # Ссылка на страницу объявления
            link = f"https://www.work.ua/ru{ad.find('a').get('href')}"
            # Наименование работодателя
            employeer = ad.find(
                'div', class_='add-top-xs').find('span').text.strip()
            # Размер заработной платы
            if ad.find('div').get('class') is None:
                salary = ad.find('div').text.strip()
                salary = salary.replace('\u202f', ' ')
                salary = salary.replace('\xa0', ' ')
            else:
                salary = 'не указана'
            # Запись полученых данных в кортеж
            ad_data = (title, employeer, link, salary)
            # Проверка записи на уникальность и запись в результирующий список
            self._checklist(ad_data)

    def _pagination(self):
        '''Изменяет ссылку на следующую страницу. Изменяет её на False, если
        следующей страницы нет'''
        # Получение ссылки на следующую странцицу
        try:
            self._url = "https://www.work.ua" + (
                self._soup.find('ul', class_='pagination')
                .find('span', class_='glyphicon-chevron-right')
                .find_parent('li').find('a').get('href')
            )
        except AttributeError:
            self._url = False


class RabotaUaParser(Parser):
    '''
    Класс определяющий методы для парсера сайта rabota.ua

    Имеет единственный публичный метод set_url(), что принимает от
    пользователя начальное значение url-адреса с которого начинается
    работа парсера
    '''

    def set_url(self, url_str):
        # Если передаваемое значение является ссылкой на hh.ru
        if url_str[:17] == 'https://rabota.ua':
            # Записываем его в соответствующее свойство объекта
            self._url = url_str

            return self

    def _get_details(self):
        '''Добавляет к списку с объявлениями новые кортежи'''
        # Находит все контейнеры с объявлениями в текущем массиве данных
        ads = self._soup.find('table', class_='f-vacancylist-tablewrap'
                              ).find_all('div', class_='card-body')
        # Находит интересующие нас данные в каждом контейнере
        for ad in ads:
            # Заголовок объявления
            title = ad.find('a', class_='ga_listing').get('title')
            # Ссылка на страницу объявления
            link = ('https://rabota.ua' +
                    ad.find('a', class_='ga_listing').get('href'))
            # Наименование работодателя
            try:
                employeer = ad.find(
                    'a', class_='company-profile-name').get('title')
            except AttributeError:
                employeer = 'не указан'

            # Размер заработной платы
            salary = ad.find('span', class_='salary').text.replace('\xa0', '')
            if salary == '':
                salary = 'не указана'
            # Запись полученых данных в кортеж
            ad_data = (title, employeer, link, salary)
            # Проверка записи на уникальность и запись в результирующий список
            self._checklist(ad_data)

    def _pagination(self):
        '''Изменяет ссылку на следующую страницу. Изменяет её на False, если
        следующей страницы нет'''
        # Получение ссылки на следующую странцицу
        try:
            self._url = 'https://rabota.ua' + self._soup.find(
                'dd', class_='nextbtn').find('a').get('href').strip()
        # Если таковой нет, то указываем это
        except AttributeError:
            self._url = False


class SuperjobParser(Parser):
    '''
    Класс определяющий методы для парсера сайта superjob.ru

    Имеет единственный публичный метод set_url(), что принимает от
    пользователя начальное значение url-адреса с которого начинается
    работа парсера
    '''

    def set_url(self, url_str):
        ''' Устанавливает стартовую ссылку для парсинга '''
        # Если передаваемое значение является ссылкой на superjob.ru
        if 'superjob.ru' in url_str and url_str[:8] == 'https://':
            # Записываем его в соответствующее свойство объекта
            self._url = url_str

            return self

    def _get_details(self):
        '''Добавляет к списку с объявлениями новые кортежи'''
        # Находит все контейнеры с объявлениями в текущем массиве данных
        ads = self._soup.find_all('div', class_='f-test-vacancy-item')
        # Находит интересующие нас данные в каждом контейнере
        for ad in ads:
            # Заголовок объявления
            title = ad.find('a', class_='_6AfZ9').text
            # Ссылка на страницу объявления
            link = ("https://www.superjob.ru" +
                    ad.find('a', class_='_6AfZ9').get('href'))
            # Наименование работодателя
            try:
                emp_class = 'f-test-text-vacancy-item-company-name'
                employeer = ad.find('span', class_=emp_class).text.strip()
            except AttributeError:
                employeer = 'не указан'
            # Размер заработной платы
            sal_class = 'f-test-text-company-item-salary'
            salary = ad.find('span', class_=sal_class).text.strip()
            salary = salary.replace('\u202f', ' ')
            salary = salary.replace('\xa0', ' ')
            # Запись полученых данных в кортеж
            ad_data = (title, employeer, link, salary)
            # Проверка записи на уникальность и запись в результирующий список
            self._checklist(ad_data)

    def _pagination(self):
        '''Изменяет ссылку на следующую страницу. Изменяет её на False, если
        следующей страницы нет'''
        # Получение ссылки на следующую странцицу
        is_next = self._soup.find('a', rel='next')
        if is_next:
            self._url = f"https://www.superjob.ru{is_next.get('href')}"
        else:
            self._url = False
