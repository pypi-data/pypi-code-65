from setuptools import setup

setup(name='Toxa',
      version='0.0.4',
      description='''
[Классы]
- Corr - класс с исправлением ошибок
- Help - класс с уменьшающий код
[Функции]
- Corr.inputs(input()) - помогает убрать все пробелы в команде input()
- Help.temo_po_name('Имя города на русском ') - возвращает  температуру города в Цельсиях
[Что нового]
- Добавлено описание
- Класс Сorr
[В планах]
- Новые классы и функции
''',
      packages=['toxa'],
      author_email='dima.terig@gmail.com',
      zip_safe=False)
