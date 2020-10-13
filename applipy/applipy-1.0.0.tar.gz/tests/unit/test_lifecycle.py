from applipy import Application, Config, AppHandle
from collections import defaultdict


class App(AppHandle):

    N = 0

    def __init__(self, call_logs: dict):
        self.call_log = call_logs[App.N]
        App.N += 1

    async def on_init(self):
        self.call_log.append('on_init')

    async def on_start(self):
        self.call_log.append('on_start')
        raise ValueError

    async def on_shutdown(self):
        self.call_log.append('on_shutdown')


def test_applipy_all_lifecyle_methods_are_called_in_the_right_order():
    app = Application(Config({}))
    call_logs = defaultdict(list)
    app.injector.bind(dict, call_logs)
    app.register(App)
    app.register(App)
    app.register(App)
    app.register(App)

    app.run()

    assert len(call_logs) == 4
    for k in call_logs:
        call_log = call_logs[k]
        assert len(call_log) == 3
        assert call_log == ['on_init', 'on_start', 'on_shutdown']
