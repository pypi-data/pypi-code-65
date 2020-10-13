import time
import collections
import threading
import warnings
import multiprocessing as mp
from .view import View
from .excs import RemoteException


__all__ = ['get', 'Proxy']


FAIL_UNPICKLEABLE = False
SELF = make_token('self')
UNDEFINED = make_token('undefined')

UNPICKLEABLE_WARNING = (
    "You tried to send an unpickleable object returned by {view} "
    "via a pipe. We'll assume this was an oversight and "
    "will return `None`. The remote caller interface "
    "is meant more for remote operations rather than "
    "passing objects. Check the return value for any "
    "unpickleable objects. "
    "The return value: {result}"
)


class _Listener:
    _thread = None
    _delay = 1e-5
    _listener_process_name = None
    _NOCOPY = ['_local', '_remote', '_llock', '_rlock', '_listening_val']
    def __init__(self, **kw):
        super().__init__(**kw)

        # cross-process objects
        self._listening_val = mp.Value('i', 0, lock=False)
        self._llock, self._rlock = mp.Lock(), mp.Lock()
        self._local, self._remote = mp.Pipe()
        self._root = self  # isn't called when extending

    def __getstate__(self):
        # NOTE: So we don't pickle queues, locks, and shared values.
        return dict(self.__dict__, _thread=None, **{k: None for k in self.NOCOPY})

    # remote calling interface

    def process_requests(self):
        '''Poll until the command queue is empty.'''
        while self._remote.poll():
            self.poll()
            time.sleep(self._delay)

    def _process(self, view):
        view = View(*view)
        result = view.resolve_view(self._obj)
        if result is self._obj:  # solution for chaining
            result = SELF
        return result

    def _local_process(self):
        return self.resolve_view(self._obj)

    def _form_request(self):
        return self._keys

    def _parse_response(self, x):
        x, exc = x
        if x == SELF:
            x = self._root  # root remote object without any ops
        if exc is not None:
            raise exc
        return x

    def _handle_no_listener(self, default=UNDEFINED):
        # if a default value is provided, then return that, otherwise return a default.
        default = self._default if default == UNDEFINED else default
        if default == UNDEFINED:
            raise RuntimeError('Remote instance is not running for {}'.format(self))
        return default

    def poll(self):
        '''Check for and execute the next command in the queue, if available.'''
        if self._remote.poll():
            with self._rlock:
                request = self._remote.recv()
                try:
                    result = self._process(request)
                except BaseException as e:
                    self._remote.send((None, RemoteException(e)))
                    return

                # result came out fine
                try:
                    self._remote.send((result, None))
                except RuntimeError as e:
                    # handle exception that happens during serialization
                    if FAIL_UNPICKLEABLE:
                        raise RuntimeError(
                            'Return value of {} is unpickleable.'.format(request)) from e
                    warnings.warn(UNPICKLEABLE_WARNING.format(view=request, result=result))
                    self._remote.send((None, None))

    # parent calling interface

    def get_(self, default=UNDEFINED):
        '''Request the remote object to evaluate the proxy and return the value.
        If you are in the same process as the remote object, it will evaluate
        directly.

        Args:
            default (any): the value to return if the remote instance isn't listening.
        '''
        if self._local_listener:  # if you're in the remote process, just run the function.
            return self._local_process()
        with self._llock:
            if self.listening_:  # if the remote process is listening, run
                # send and wait for a result
                self._local.send(self._form_request())
                x = self._local.recv()
                if x is not None:
                    return self._parse_response(x)

        return self._handle_no_listener(default=default)

    @property
    def _local_listener(self):
        '''Is the current process the main process or a child one?'''
        return mp.current_process().name == self._listener_process_name

    # running state - to avoid dead locks, let the other process know if you will respond

    @property
    def listening_(self):
        '''Is the remote instance listening?'''
        return bool(self._listening_val.value)

    @listening_.setter
    def listening_(self, value):
        # set first so no one else can
        prev = self.listening_
        self._listening_val.value = int(value)
        self._listener_process_name = mp.current_process().name if value else None
        # make sure no one is left waiting.
        if prev and not value:
            if self._fulfill_final:
                self.process_requests()
            else:
                while self._remote.poll():
                    _ = self._remote.recv()
                    self._remote.send(None)  # cancel

    # remote background listening interface
    '''

    do (clean, easy, runs in background)
    >>> with self.remote.listen_(bg=True):  # automatic
    ...     ...  # don't have to poll

    or (runs in background, manual cleanup)
    >>> self.remote.listen_(bg=True)  # automatic
    >>> ...  # don't have to poll
    >>> self.remote.stop_listen_()

    or (clean, easy, more control)
    >>> with self.remote.listen_():  # manual
    ...     while True:
    ...         self.remote.poll()  # need to poll, otherwise they'll hang

    or when you've got nothing else to do
    >>> self.remote._run_listener()

    '''

    _thread_exception = None
    def listen_(self, bg=False):
        '''Start a background thread to handle requests.'''
        self._thread_exception = None
        if not bg:
            self.listening_ = True
            return self

        if self._thread is None:
            self._thread = threading.Thread(
                target=self._run_listener, kwargs={'_catch_exc': True}, daemon=True)
            self._thread.start()
        return self

    def stop_listen_(self):
        '''Set listening to False. If a thread is running, close it.'''
        self.listening_ = False
        if self._thread is not None:
            self._thread.join()
        self._thread = None
        if self._thread_exception is not None:
            raise self._thread_exception
        return self

    def _run_listener(self, _catch_exc=True):
        '''Run the listener loop. This is what is run in the thread.'''
        try:
            self.listening_ = True
            while self.listening_:
                self.process_requests()
                time.sleep(self._delay)
        except Exception as e:
            if not _catch_exc:
                raise
            self._thread_exception = e
        finally:
            self.listening_ = False

    def wait_until_listening(self, proc=None, fail=True):
        '''Wait until the remote instance is listening.

        Args:
            proc (mp.Process): If passed and the process dies, raise an error.
            fail (bool): Should it raise an exception if the process dies?
                Otherwise it would just return `False`.

        Returns:
            Whether the process is listening.

        Raises:
            `RuntimeError if fail == True and not proc.is_alive()`
        '''
        while not self.listening_:
            if proc is not None and not proc.is_alive():
                if fail:
                    raise RuntimeError('Process is dead and the proxy never started listening.')
                return False
            time.sleep(self._delay)
        return True

    def __enter__(self):
        self.listening_ = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_listen_()
