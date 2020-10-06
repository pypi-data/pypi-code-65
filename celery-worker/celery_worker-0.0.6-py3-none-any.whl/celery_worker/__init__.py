from celery import Celery


class CeleryWorker(object):
    def __init__(self, name, conf):
        self.__instance = Celery(name)
        self.__instance.conf.update(conf)

    def register(self, task):
        self.__instance.tasks.register(task)

    def start(self):
        self.__instance.start(argv=['celery', 'worker', '--beat', '-l', 'info'])

    def purge(self):
        self.__instance.start(argv=['celery', 'purge', '-f'])

    def publish(self, task, message):
        self.__instance.send_task(task, [message])
