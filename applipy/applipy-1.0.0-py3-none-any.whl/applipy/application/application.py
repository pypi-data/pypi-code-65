import signal
import traceback

from typing import Union, Callable, Type, Optional, TypeVar, Any
from asyncio import gather, get_event_loop, Task, BaseEventLoop, CancelledError
from logging import Logger, INFO, ERROR, getLevelName
from applipy.application.apphandle import AppHandle
from applipy.application.module import Module
from applipy.config.config import Config
from applipy_inject import Injector


T = TypeVar('T')
BindFunction = Callable[
    [
        Type[T],
        Union[T, Callable[[Any], T]],
        Optional[str],
        Optional[bool]
    ],
    None
]
RegisterFunction = Callable[[Module], None]


class ModuleManager:

    def __init__(self, injector: Injector) -> None:
        self._injector = injector
        self._modules = set()

    def install(self, module: Type[Module]) -> 'ModuleManager':
        if module not in self._modules:
            self._modules.add(module)
            self._injector.bind_provider(Module, module)
            for dep in module.depends_on():
                self.install(dep)

        return self

    def configure_all(self, bind_function: BindFunction,
                      register_function: RegisterFunction) -> None:
        instances = self.injector.get_all(Module)
        for instance in instances:
            instance.configure(bind_function, register_function)
            self._log(INFO, f'Installing module `{instance.__class__.__module__}.{instance.__class__.__name__}`')

        self._modules = set()

    @property
    def injector(self):
        return self._injector

    def _log(self, level, *args, **kwargs):
        try:
            self._injector.get(Logger).log(level, *args, **kwargs)
        except Exception:
            print(f"[{getLevelName(level)}]", *args)


class EventLoopManager:

    def __init__(self, loop=None):
        self._loop = loop or get_event_loop()

    def run(self, coro):
        self._loop.run_until_complete(coro)

    def shutdown(self):
        self.cancel_loop_tasks()
        self._close_loop()

    def _close_loop(self):
        self._loop.run_until_complete(self._loop.shutdown_asyncgens())
        self._loop.close()

    def cancel_loop_tasks(self):
        tasks_to_cancel = {t for t in Task.all_tasks(self._loop)
                           if not t.done()}
        if not tasks_to_cancel:
            return

        for t in tasks_to_cancel:
            t.cancel()


AppHandleProvider = Union[Type[AppHandle], Callable[[], AppHandle]]


class AppHandleManager:

    def __init__(self, injector: Injector, loop: BaseEventLoop) -> None:
        self._injector = injector
        self._loop = loop

    def register(self,
                 app_handle_provider: AppHandleProvider) -> 'AppHandleManager':
        self._injector.bind_provider(AppHandle, app_handle_provider)

    async def init_all(self):
        app_handles = self._injector.get_all(AppHandle)
        await gather(*(app_handle.on_init() for app_handle in app_handles),
                     loop=self._loop)

    async def start_all(self):
        app_handles = self._injector.get_all(AppHandle)
        await gather(*(app_handle.on_start() for app_handle in app_handles),
                     loop=self._loop)

    async def shutdown_all(self):
        app_handles = self._injector.get_all(AppHandle)
        await gather(*(app_handle.on_shutdown() for app_handle in app_handles),
                     loop=self._loop)


class Application:

    def __init__(self,
                 config,
                 injector=None,
                 event_loop_manager=None,
                 module_manager=None,
                 app_handle_manager=None,
                 loop=None,
                 signal_=None):
        self._config = config

        loop = loop or get_event_loop()
        self._injector = injector or Injector()

        self._event_loop_manager = event_loop_manager or EventLoopManager(loop)
        self._app_handle_manager = (app_handle_manager or
                                    AppHandleManager(self._injector, loop))

        self._module_manager = module_manager or ModuleManager(self._injector)

        def _sigterm_handler():
            self._log(INFO, "Received SIGTERM. Shutting down.")
            self._event_loop_manager.cancel_loop_tasks()

        def _sigint_handler():
            self._log(INFO, "Received SIGINT. Shutting down.")
            self._event_loop_manager.cancel_loop_tasks()

        loop.add_signal_handler(signal.SIGTERM, _sigterm_handler)
        loop.add_signal_handler(signal.SIGINT, _sigint_handler)

    def install(self, module):
        self._module_manager.install(module)
        return self

    def register(self, app_handle_provider):
        self._app_handle_manager.register(app_handle_provider)
        return self

    @property
    def injector(self):
        return self._injector

    def run(self):
        self._injector.bind(Config, self._config)
        self._module_manager.configure_all(
            self._injector.bind,
            self._app_handle_manager.register
        )
        self._event_loop_manager.run(self._run_application())
        self._event_loop_manager.shutdown()

    async def _run_application(self):
        try:
            await self._app_handle_manager.init_all()
            await self._app_handle_manager.start_all()
        except CancelledError:
            pass
        except Exception:
            self._log(ERROR, traceback.format_exc())
        finally:
            await self._app_handle_manager.shutdown_all()

    def _log(self, level, *args, **kwargs):
        try:
            self._injector.get(Logger).log(level, *args, **kwargs)
        except Exception:
            print(f"[{getLevelName(level)}]", *args)
