from datetime import datetime
from typing import List

from . import cmd

import logging
import coloredlogs

__PRIMITIVES__ : List[str] = []
__HEADER_MAX_SIZE__ : int = 0

def _print_impl(header, content):
    print(header + "$ " + content)

def _get_header(code : int):
    header = "> "
    header += datetime.now().strftime("%H:%M:%S")
    header += " - "
    header += "["
    header += ("{:>" + str(__HEADER_MAX_SIZE__) + "}").format(
            __PRIMITIVES__[code])
    header += "] "
    return header

def register_primitive(primitive : str) -> int:
    global __PRIMITIVES__, __HEADER_MAX_SIZE__

    code = len(__PRIMITIVES__)
    if len(primitive) > __HEADER_MAX_SIZE__:
        __HEADER_MAX_SIZE__ = len(primitive)
    __PRIMITIVES__.append(primitive)
    return code

COMMAND = register_primitive("COMMAND")
HEADER = register_primitive("========== HEADER ==========")

INFO = register_primitive("INFO")
DEBUG = register_primitive("DEBUG")
WARN = register_primitive("WARN")
ERROR = register_primitive("ERROR")
FATAL = register_primitive("FATAL")

def Print(code, *args):
    global __PRIMITIVES__

    if code >= len(__PRIMITIVES__):
        raise RuntimeError("out of bound primitive code: " + code)

    header = _get_header(code)
    content = " ".join(args)
    _print_impl(header, content)

class ColorFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super(ColorFormatter, self).__init__(fmt, datefmt, style)

        self._colors = {
            "TRACE": "\033[38;5;111m",
            "DEBUG": "\033[38;5;111m",
            " INFO": "\033[38;5;47m",
            " WARN": "\033[38;5;178m",
            "ERROR": "\033[38;5;196m",
            "FATAL": "\033[30;48;5;196m",
        }
        self._default = "\033[38;5;15m"
        self._reset = "\033[0m"

    def format(self, record):
        message = super(ColorFormatter, self).format(record)
        log_color = self._colors.get(record.levelname, self._default)
        message = log_color + message + self._reset
        return message

class FilterList(logging.Filter):
    """ Filter with logging module

        Filter rules as below:
            {allow|disable log name} > level no > keywords >
            {inheritance from parent log name} > by default filter
        TODO:
    """
    def __init__(self, default=False, allows=[], disables=[],
            keywords=[], log_level=logging.INFO):
        self.rules = {}
        self._internal_filter_rule = "_internal_filter_rule"
        self.log_level = log_level
        self.keywords = keywords

        self.rules[self._internal_filter_rule] = default
        for name in allows:
            splits = name.split(".")
            rules = self.rules
            for split in splits:
                if split not in rules:
                    rules[split] = {}
                rules = rules[split]

            rules[self._internal_filter_rule] = True

        for name in disables:
            splits = name.split(".")
            rules = self.rules
            for split in splits:
                if split not in rules:
                    rules[split] = {}
                rules = rules[split]

            rules[self._internal_filter_rule] = False

    def filter(self, record):
        rules = self.rules
        rv = rules[self._internal_filter_rule]

        splits = record.name.split(".")
        for split in splits:
            if split in rules:
                rules = rules[split]
                if self._internal_filter_rule in rules:
                    rv = rules[self._internal_filter_rule]
            else:
                if record.levelno >= self.log_level:
                    return True

                for keyword in self.keywords:
                    if keyword in record.getMessage():
                        return True
                return rv
        return rv

TRACE = logging.DEBUG // 2
DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERROR = logging.ERROR
FATAL = logging.CRITICAL

logging.addLevelName(TRACE, "TRACE")
logging.addLevelName(DEBUG, "DEBUG")
logging.addLevelName(INFO, " INFO")
logging.addLevelName(WARN, " WARN")
logging.addLevelName(ERROR, "ERROR")
logging.addLevelName(FATAL, "FATAL")

__LOG_VERBOSITY__ = [TRACE, DEBUG, INFO, WARN, ERROR, FATAL]
__LOG_IDX__ = list(range(len(__LOG_VERBOSITY__)))
__LOG_NAME__ = ",".join([logging.getLevelName(l).strip() \
    + "(" + str(n) + ")" \
    for l, n in zip(__LOG_VERBOSITY__, __LOG_IDX__)])

@cmd.register_option("-v", "--verbosity",
                     type=int,
                     choices=__LOG_IDX__,
                     default=0,
                     help="the verbosity for log level, " +
                        "show level upper set by user, "
                        "corresponding with " + __LOG_NAME__)
@cmd.mod_ref("log")
def Init(args):
    log_level = __LOG_VERBOSITY__[args.verbosity]
    logging.basicConfig(level=log_level)
    formatter = ColorFormatter(
            fmt="[ %(asctime)s %(name)s %(levelname)s ] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")

    log_filter = FilterList(
                log_level=log_level,
                default=False)
    for handler in logging.root.handlers:
        handler.addFilter(log_filter)
        handler.setFormatter(formatter)

    logging.info("log module initiate with level: %s",
                 logging.getLevelName(log_level))

@cmd.mod_main("log", help="log test module")
def test_main(args):
    print(args)

    print(cmd.ParserStorage.iterate())
    Init(args)
    logging.debug("test")
    logging.info("test")
    logging.warning("test")
    logging.error("test")


if __name__ == "__main__":
    cmd.Run()
