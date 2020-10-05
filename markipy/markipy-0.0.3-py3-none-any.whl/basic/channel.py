from queue import Queue


class Channel:

    def __init__(self, size=12500):
        self.queue_size = size
        self.queue = None
        self.finish = False
        self.channel = Queue(self.queue_size)
        self.empty = Queue.empty

    def get(self):
        try:
            return self.channel.get(block=True, timeout=5)
        except Exception as e:
            return self.empty

    def put(self, var):
        self.channel.put(var, block=True)

    def task_done(self):
        self.channel.task_done()

    def set_finish(self):
        self.finish = True

    def get_finish(self):
        return self.finish

    def wait_completion_task(self):
        self.channel.join()
        self.set_finish()
