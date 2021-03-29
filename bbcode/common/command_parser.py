from __future__ import annotations

from typing import Sequence, Dict
from typing import Callable

import argparse

parser = argparse.ArgumentParser(
    description="bbcode helper script, implemented via python3")

__PARSER_KEY__ = "__PARSER__"
__SUB_PARSER_KEY__ = "__SUB_PARSER__"

""" Parser Root Object Dict

    orginized as like tree format, and each node maintains a default
    parser via key:`__PARSER__`.
"""
__PARSERS__ = { __PARSER_KEY__: parser }

def _register_sub_parser(parser_object : Dict, name, **kw):
    if __SUB_PARSER_KEY__ not in parser_object:
        parser_object[__SUB_PARSER_KEY__] = \
            parser_object[__PARSER_KEY__].add_subparsers(
                title="COMMAND",
                description="collective sub commands",
            )
    sub_parser = parser_object[__SUB_PARSER_KEY__]
    module_parser = sub_parser.add_parser(name, **kw)
    parser_object[name] = { __PARSER_KEY__: module_parser }

def _get_parser(parser_path : str, check_error : bool = False, **kw):
    paths = parser_path.split(".")
    paths = [p for p in paths if p]

    parser_object = __PARSERS__
    for p in paths:
        if p not in parser_object:
            if check_error:
                raise RuntimeError(
                        "parser path invalid {}".format(parser_path))
            else:
                _register_sub_parser(parser_object, p, **kw)
        parser_object = parser_object[p]
    return parser_object[__PARSER_KEY__]

class ParserFunc:
    def __init__(self, parser):
        self._parser = parser
        self._func = None
        self._opt_funcs = {}

    def __call__(self, param) -> ParserFunc:
        if callable(param): # register module func
            self._func = param
            self._parser.set_defaults(func=self)
            return self
        else: # invoke module func
            return self._func_call(param)

    def option(self, *args, **kw):
        self._parser.add_argument(*args, **kw)

    def register_option_func(self, func):
        name = func.__name__.replace("_", "-")
        desc = func.__doc__
        self._parser.add_argument(
            "--" + name,
            action="store_true",
            help=desc)
        self._opt_funcs[name] = func
        return self

    def _func_call(self, args):
        for arg_name, func in self._opt_funcs.items():
            if getattr(args, arg_name.replace("-", "_")):
                return func(args)
        return self._func(args)

def option(*args, **kw):
    def _option(pfunc : ParserFunc) -> ParserFunc:
        pfunc.option(*args, **kw)
        return pfunc
    return _option

def mod_parser(parser_path : str = "", **kw) -> ParserFunc:
    parser = _get_parser(parser_path, **kw)
    pfunc = ParserFunc(parser)
    return pfunc

test_parser = mod_parser("test", help="enable test module")

@test_parser
def TestCore(args):
    print("Test Call")

@option("--enableA", action="store_true", help="enableA opt1 flag")
@option("--enableB", action="store_true", help="enableB opt1 flag")
@test_parser.register_option_func
def test_opt1(args):
    """ test opt1 helper func
    """
    if args.enableB:
        print("enable flag opt1")
    else:
        print("disable flag opt1")

tp1 = mod_parser("test")
@tp1.register_option_func
def test_opt2(args):
    print("test opt2")

if __name__ == "__main__":
    args = parser.parse_args()
    if getattr(args, "func", None):
        args.func(args)
        exit(0)

