from datetime import datetime
from typing import List

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
INFO = register_primitive("INFO")
DEBUG = register_primitive("DEBUG")
WARN = register_primitive("WARN")
ERROR = register_primitive("ERROR")

def Print(code, *args):
    global __PRIMITIVES__

    if code >= len(__PRIMITIVES__):
        raise RuntimeError("out of bound primitive code: " + code)

    header = _get_header(code)
    content = " ".join(args)
    _print_impl(header, content)
