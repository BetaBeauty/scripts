import os
import sys
import logging
import signal
from threading import Event, Thread

__QUIT_EVENTS__ = []

def as_thread_func(func):
    def _container(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs)
        t.start()
        return t
    return _container

def wait_or_exit(timeout):
    event = Event()
    __QUIT_EVENTS__.append(event)
    event.wait(timeout)
    __QUIT_EVENTS__.remove(event)

    if event.is_set():
        os.sys.exit()

# service module

__REGISTER_SERVICES__ = {}
logger = logging.getLogger("service")

class ThreadFunc:
    def __init__(self, name, serve=False, timeout=5):
        self._name = name
        self._serve = serve
        self._time_out = timeout
        self._func = None
        self._stop = None

    def register_func(self, func):
        def _func(*args, **kw):
            status = func(*args, **kw)
            status = True if status is None else bool(status)
            while self._serve and (not status):
                logger.warning(" ".join([
                    "service {} stopped for unknown error,".format(
                        self._name),
                    "restart in {} seconds".format(self._time_out)
                ]))
                wait_or_exit(self._time_out)
                status = func(*args, **kw)
        self._func = as_thread_func(_func)

    def register_stop_func(self, func):
        self._stop = func

    def start(self, *args, **kw):
        if self._func is None:
            return
        return self._func(*args, **kw)

    def stop(self):
        if self._stop is not None:
            self._stop()

""" Server Function

    Returns
    =======
    status: bool
"""

def register_service(name, **kw):
    def _func(func):
        tfunc = ThreadFunc(name, **kw)
        if name in __REGISTER_SERVICES__:
            raise RuntimeError("duplicated service function")
        __REGISTER_SERVICES__[name] = tfunc
        tfunc.register_func(func)
        return func
    return _func

def register_stop_handler(name):
    if name not in __REGISTER_SERVICES__:
        raise RuntimeError("invalid service name: {}".format(name))

    def _func(func):
        __REGISTER_SERVICES__[name].register_stop_func(func)
        return func
    return _func

def auto_close():
    def _shut_down(signo=2, _frame=None):
        print("\n")
        logger.info("shutting down ...")
        for event in __QUIT_EVENTS__:
            event.set()

        for name, func in __REGISTER_SERVICES__.items():
            logger.info("stop service - {}".format(name))
            func.stop()

    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(
            getattr(signal, 'SIG'+sig),
            _shut_down);

def Run(*args, **kw):
    auto_close()

    for name, func in __REGISTER_SERVICES__.items():
        logger.info("start service - {}".format(name))
        func.start(*args, **kw)
