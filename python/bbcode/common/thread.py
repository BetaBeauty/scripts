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
    def __init__(self, name):
        self._name = name
        self._func = None
        self._stop = None

    def register_func(self, func,
                      auto_reload=False,
                      timeout=5):
        if self._func is not None:
            raise RuntimeError(
                "service:{} has been registered".format(self._name))

        self._auto_reload = auto_reload
        self._time_out = timeout

        def catch_func(*args, **kw):
            try:
                func(*args, **kw)
            except Exception as e:
                logger.error(
                    "service:{} raise exception: {}".format(
                        self._name, e))

        def wrapper_func(*args, **kw):
            catch_func(*args, **kw)

            while self._auto_reload:
                logger.warning(" ".join([
                    "service {} closed,".format(
                        self._name),
                    "restart in {} seconds".format(self._time_out)
                ]))
                # clear service context
                if self._stop is not None:
                    self._stop()
                wait_or_exit(self._time_out)

                catch_func(*args, **kw)
        self._func = as_thread_func(wrapper_func)

    def register_stop_func(self, func):
        self._stop = func

    def serve(self, *args, **kw):
        if self._func is None:
            raise RuntimeError(
                "service:{} has not been registered".format(self._name))
            return
        return self._func(*args, **kw)

    def close(self):
        self._auto_reload = False
        if self._stop is not None:
            self._stop()

def register_service(name, **kw):
    def _func(func):
        __REGISTER_SERVICES__.setdefault(name, ThreadFunc(name))
        __REGISTER_SERVICES__[name].register_func(func, **kw)
        return func
    return _func

def register_stop_handler(name):
    def _func(func):
        __REGISTER_SERVICES__.setdefault(name, ThreadFunc(name))
        __REGISTER_SERVICES__[name].register_stop_func(func)
        return func
    return _func

def auto_close():
    def _shut_down(signo=2, _frame=None):
        print("")
        logger.info("shutting down ...")
        for event in __QUIT_EVENTS__:
            event.set()

        for name, func in __REGISTER_SERVICES__.items():
            logger.info("stop service - {}".format(name))
            func.close()

    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(
            getattr(signal, 'SIG'+sig),
            _shut_down);

def Run(*args, **kw):
    auto_close()

    for name, func in __REGISTER_SERVICES__.items():
        logger.info("start service - {}".format(name))
        func.serve(*args, **kw)
