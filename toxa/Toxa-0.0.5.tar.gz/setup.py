from setuptools import setup

setup(name='Toxa',
      version='0.0.5',
      description='''
[Классы]\n
- Corr - класс с исправлением ошибок\n
- Help - класс с уменьшающий код\n
[Функции]\n
- Corr.inputs(input()) - помогает убрать все пробелы в команде input()\n
- Help.temo_po_name('Имя города на русском ') - возвращает  температуру города в Цельсиях\n
[Что нового]\n
- Добавлено описание\n
- Класс Сorr\n
[В планах]\n
- Новые классы и функции\n
''',
      home_page='',
      author='Toxa',
      packages=['toxasup'],
      author_email='dima.terig@gmail.com',
      zip_safe=False)
