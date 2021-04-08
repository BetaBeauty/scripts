import os
import sys
import logging
import signal
from threading import Event, Thread

_QUIT_EVENT_ = Event()

def as_thread_func(func):
    def _container(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs)
        t.start()
        return t
    return _container

def wait(timeout):
    _QUIT_EVENT_.wait(timeout)

    if _QUIT_EVENT_.is_set():
        os.sys.exit()

# service module

__REGISTER_SERVICES__ = {}
logger = logging.getLogger("service")

class ThreadFunc:
    def __init__(self, func):
        self._func = as_thread_func(func)
        self._stop = None

    def register_stop_func(self, func):
        self._stop = func

    def start(self, *args, **kw):
        return self._func(*args, **kw)

    def stop(self):
        if self._stop is not None:
            self._stop()

def register_service(name):
    def _func(func):
        __REGISTER_SERVICES__[name] = ThreadFunc(func)
        return func
    return _func

def register_stop_handler(name):
    if name not in __REGISTER_SERVICES__:
        raise RuntimeError("inliva service name:" + name)

    def _func(func):
        __REGISTER_SERVICES__[name].register_stop_func(func)
        return func
    return _func

def _stop_service(signo=2, _frame=None):
    logger.info("shutting down ...")
    _QUIT_EVENT_.set()

    for name, func in __REGISTER_SERVICES__.items():
        logger.info("stop service - {}".format(name))
        func.stop()

def Run(*args, **kw):
    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(
            getattr(signal, 'SIG'+sig),
            _stop_service);

    for name, func in __REGISTER_SERVICES__.items():
        logger.info("start service - {}".format(name))
        func.start(*args, **kw)
