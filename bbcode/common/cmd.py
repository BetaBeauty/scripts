from __future__ import annotations

from typing import Sequence, Dict
from typing import Callable

import argparse

parser = argparse.ArgumentParser(
    description="bbcode helper script, implemented via python3")

class ParserStorage:
    __PARSER_KEY__ = "__PARSER__"
    __SUB_PARSER_KEY__ = "__SUB_PARSER__"
    __GROUP_PARSER_KEY__= "__GROUP_PARSER__"
    __FUNC_KEY__ = "__FUNC__"

    """ Parser Root Object Dict

        orginized as like tree format, and each node maintains a default
        parser via key:`__PARSER__`.
    """
    __STORES__ = {
        __PARSER_KEY__: parser,
        __GROUP_PARSER_KEY__: {},
    }

    @staticmethod
    def _init_parser_object(parser, is_group=False):
        parser_object = {
            ParserStorage.__PARSER_KEY__: parser,
        }
        if not is_group:
            parser_object[ParserStorage.__GROUP_PARSER_KEY__] = {}
        return parser_object

    @staticmethod
    def get_parser_object(
            parser_path : str,
            group_name : str = "",
            parser_opts : Sequence[Dict] = []):
        paths = [p for p in parser_path.split(".") if p]
        parser_object = ParserStorage.__STORES__

        left_paths = []
        for idx, p in enumerate(paths):
            if p not in parser_object:
                left_paths = paths[idx:]
                break
            parser_object = parser_object[p]

        # process left path parser
        for _ in range(len(parser_opts), len(left_paths) + 1):
            parser_opts.append({})

        for p, opt in zip(left_paths, parser_opts[:-1]):
            parser_object = ParserStorage.register_parser(
                parser_object, p, opt)

        if group_name:
            if group_name not in parser_object[__GROUP_PARSER_KEY__]:
                ParserStorage.register_group(
                    parser_object, group_name, parser_opt[-1])
            parser_object = parser_object[__GROUP_PARSER_KEY__][group_name]
        return parser_object

    @staticmethod
    def register_parser(parser_object, name, parser_opt = {}):
        if ParserStorage.__SUB_PARSER_KEY__ not in parser_object:
            parser = parser_object[ParserStorage.__PARSER_KEY__]
            parser_object[ParserStorage.__SUB_PARSER_KEY__] = \
                parser.add_subparsers(
                    title="COMMAND",
                    description="collective sub commands",
                )

        if name in parser_object:
            raise RuntimeError("parser " + name + " has been registered")

        sub_parser = parser_object[ParserStorage.__SUB_PARSER_KEY__]
        mod_parser = sub_parser.add_parser(name, **parser_opt)
        parser_object[name] = ParserStorage._init_parser_object(mod_parser)
        return parser_object[name]

    @staticmethod
    def register_group(parser_object, name, parser_opt = {}):
        parser = parser_object[ParserStorage.__PARSER_KEY__]
        gparser = parser.add_argument_group(
            name, **parser_opt)

        if name in parser_object[ParserStorage.__GROUP_PARSER_KEY__]:
            raise RuntimeError("group parser " + name + " has been registered")

        parser_object[ParserStorage.__GROUP_PARSER_KEY__][name] = \
            ParserStorage._init_parser_object(gparser, is_group=True)
        return parser_object[ParserStorage.__GROUP_PARSER_KEY__][name]

    @staticmethod
    def register_func(parser_object, func):
        if ParserStorage.__FUNC_KEY__ in parser_object:
            raise RuntimeError(
                "duplicated function set in parser storage, " +
                "func-name: " + func.__name__ + " " +
                "with storage: " + str(parser_object)
            )
        parser_object[ParserStorage.__FUNC_KEY__] = func

    @staticmethod
    def get_parser_from_object(parser_object):
        return parser_object[ParserStorage.__PARSER_KEY__]

    @staticmethod
    def list_group_name(parser_object):
        return parser_object[ParserStorage.__GROUP_PARSER_KEY__].keys()

    @staticmethod
    def get_func(parser_object, group_name : str = ""):
        group_parsers = parser_object[ParserStorage.__GROUP_PARSER_KEY__]
        if group_name and group_name in group_parsers and \
                ParserStorage.__FUNC_KEY__ in group_parsers[group_name]:
            return group_parsers[group_name][ParserStorage.__FUNC_KEY__]

        if not group_name and \
                ParserStorage.__FUNC_KEY__ in parser_object:
            return parser_object[ParserStorage.__FUNC_KEY__]

        def _null_func(*args, **kw):
            print("null module function")
        return _null_func

class ParserFunc:
    """ Options orginized as argument group
    """

    def __init__(self, parser_object):
        self._parser_object = parser_object
        self._parser = ParserStorage.get_parser_from_object(parser_object)

        self._is_ref = False
        self._func = None

    def by_reg(self, func):
        self._parser.set_defaults(func=self)
        ParserStorage.register_func(self._parser_object, func)
        return self

    def by_ref(self, func):
        self._is_ref = True
        self._func = func
        return self

    def __call__(self, *args, **kw):
        if self._is_ref:
            self._func(*args, **kw)
        else:
            self._mod_call(*args, **kw)

    def _mod_call(self, args):
        names = ParserStorage.list_group_name(self._parser_object)

        is_group_func = False
        for group_name in names:
            if getattr(args, group_name.replace("-", "_"), None):
                func = ParserStorage.get_func(self._parser_object, group_name)
                func(args)
                is_group_func = True

        if not is_group_func:
            ParserStorage.get_func(self._parser_object)(args)

    def register_option(self, *args, **kw):
        self._parser.add_argument(*args, **kw)

    def by_group(self, func):
        name = func.__name__.replace("_", "-")
        desc = func.__doc__
        gp_object = ParserStorage.register_group(
            self._parser_object, name,
            parser_opt = { "description": desc })
        gparser = ParserStorage.get_parser_from_object(gp_object)

        arg_name = "--" + name
        gparser.add_argument(
            arg_name,
            action="store_true",
            help="enable module " + name)

        return ParserFunc(gp_object)

def register_option(*args, **kw):
    def _option(pfunc : ParserFunc) -> ParserFunc:
        pfunc.register_option(*args, **kw)
        return pfunc
    return _option

def mod_ref(parser_path : str = "", **kw) -> ParserFunc:
    parser = ParserStorage.get_parser_object(parser_path, parser_opts=[kw])
    return ParserFunc(parser).by_ref

def mod_main(parser_path : str = "", **kw):
    parser = ParserStorage.get_parser_object(parser_path, parser_opts=[kw])
    return ParserFunc(parser).by_reg

def group_ref(parser_path : str = "", **kw):
    parser = ParserStorage.get_parser_object(parser_path, parser_opts=[kw])
    def _ref(func):
        return ParserFunc(parser).by_group(func).by_ref(func)
    return _main

def group_main(parser_path : str = "", **kw):
    parser = ParserStorage.get_parser_object(parser_path, parser_opts=[kw])
    def _main(func):
        return ParserFunc(parser).by_group(func).by_reg(func)
    return _main

def Run():
    args = parser.parse_args()

    if getattr(args, "func", None):
        args.func(args)
        exit(0)

    raise RuntimeError(
        "cannot find the mainly function to run, " +
        "please set main function via mod_main or group_main."
    )

# test_parser = mod_parser("test", help="enable test module")

# @test_parser
# def TestCore(args):
    # print("Test Call")

# @register_option("--enableA", help="enableA opt1 flag")
# @register_option("--enableB", action="store_true", help="enableB opt1 flag")
# @mod_group("test")
# def test_opt1(args):
    # """ test opt1 helper func
    # """
    # if args.enableB:
        # print("enable flag opt1")
    # else:
        # print("disable flag opt1")

if __name__ == "__main__":
    Run()

