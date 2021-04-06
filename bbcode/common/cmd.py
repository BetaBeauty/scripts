from __future__ import annotations

from typing import Sequence, Dict
from typing import Callable

import copy
from enum import Enum

import argparse

root_parser = argparse.ArgumentParser(
    add_help=False,
    description="bbcode helper script, implemented via python3")


""" BBCode CMD Module Design

    The target is to auto inject command line parser into registry
    table with the python decorator syntax, and the module could
    collect the neccessary options and print usage with `-h` option.

    User try to invoke the main function: `Run` to start customized
    application, which will auto run the appropriate module function.

    >>> from bbcode.common import cmd
    >>> cmd.Run()

    Interfaces
    ==========
    @func Run: Mainly program entry function
    @func mod_ref: Module reference function to register options,
        which accepts the same arguments as
        `logging.ArgumentParser.add_argument`.
    @func mod_main: Module main entry function, the releated function
        will trigger after the command line set name.

        One notable thing to be indicated is that the dependencies
        between modules should not contains cycle, or will raise
        runtime error. The dependent module's options will be treated
        as group reference, and group options will be copied into
        current module's group options.

        @param refs: List of module string, auto combine module options
            by referece to with current module.
    @func group_ref: Group reference function.
    @func group_main: Group main function, which will be execute
        multiple times if set in command line.
"""

class LogName:
    """ Formatted Logger Name

        1. Dot splitted name, aka "cmd.test"
        2. Array for module names, aka ["cmd", "test"]
        3. Group related name, aka "cmd-test", always with prefix:"--"
        4. Argument name parsed from command line, aka "cmd_test"
    """

    def __init__(self, log_name : str):
        assert "-" not in log_name, log_name
        assert "_" not in log_name, log_name
        self.name = log_name

    def __repr__(self):
        return self.name

    # hashable type, can be used at dict type
    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other : LogName):
        if isinstance(other, str):
            other = LogName(other)
        return other.name == self.name

    @staticmethod
    def from_mod_array(mod_arr : Sequence[str]) -> LogName:
        return LogName(".".join(mod_arr))

    @staticmethod
    def from_cmd_name(cmd_name : str) -> LogName:
        return LogName(cmd_name.replace("-", "."))

    @staticmethod
    def from_arg_name(arg_name : str) -> LogName:
        return LogName(arg_name.replace("_", "."))

    @property
    def mod_array(self):
        return [n for n in self.name.split(".") if n]

    @property
    def mod_prefix_arr(self):
        prefix_arr = []
        for i in range(len(self.mod_array)):
            prefix_arr.append(".".join(self.mod_array[:i+1]))
        return prefix_arr

    @property
    def mod_name(self):
        return self.name.replace(".", "-")

    @property
    def cmd_name(self):
        return "--" + self.name.replace(".", "-")

    @property
    def arg_name(self):
        return self.name.replace(".", "_")

class LogOption:
    def __init__(self):
        self.is_init = False
        self.args = []
        self.kw = {}

    def register(self, args, kw):
        self.is_init = True
        self.args = args
        self.kw = kw
        return self

    def __repr__(self):
        return "@Opt(%s,%s)" % (self.args, self.kw)

class EntryType(Enum):
    GLOBAL = 0
    MODULE = 1

    # module as public entry function.
    PUB_MOD = 0
    # module as protected entry function,
    #   but group options will pass through as public.
    PRO_MOD = 1
    # module as private entry function, options will be private as same.
    PRI_MOD = 2
    # public options reference.
    PUB_REF = 3
    # options to be private for current module.
    PRI_REF = 4

    @staticmethod
    def is_mod(entry_type):
        return entry_type in [PUB_MOD, PRO_MOD, PRI_MOD]

    @staticmethod
    def is_public(entry_type):
        return entry_type 

class LogFunction:
    def __init__(self, entry):
        self.entry : LogEntry = entry
        self.func = None
        self.is_main = False

    def __repr__(self):
        func_type = "MAIN" if self.is_main else "PASS"
        return "%s (%s)" % (func_type, self.func)

    def __call__(self, *args, **kw):
        if self.func is None and EntryType.is_mod(self.entry.entry_type):
            raise RuntimeError("cannot find the main function to run")

        if self.func is None:
            print("null module function")
        else:
            return self.func(*args, **kw)

    def wrapper(self, func):
        self.func = func
        return self

    def empty(self) -> bool:
        return self.func is None

class LogEntry:
    def __init__(self, name : LogName, entry_type : EntryType):
        self.name : LogName = name
        self.entry_type = entry_type
        self.options : Sequence[LogOption] = []
        self.params : LogOption = LogOption()
        self.func : LogFunction = LogFunction(self)
        self.groups : Dict[LogName, LogEntry] = {}

    def to_string(self, new_line=False, print_simple=True):
        prefix = "\n\t" if new_line else " | "

        ser = "Name=%s" % self.name
        ser += prefix + "Params=%s" % self.params
        ser += prefix + "Options=%s" % self.options
        if print_simple:
            group_ser = ", ".join(v.name for v in self.groups.values())
        else:
            group_ser = ",\n\t".join([v.to_string() \
                for v in self.groups.values()])
            group_ser = "\n\t" + group_ser + "\n"
        ser += prefix + "Groups=[%s] " % group_ser
        return ser

    def add_group_entry(self, entry) -> LogEntry:
        if entry.name in self.groups:
            raise RuntimeError("group " + entry.name + " has been registered")
        self.groups[entry.name] = entry
        return self.groups[entry.name]

    def as_group_opt(self, is_group=False):
        entry = LogEntry(self.name, entry_type=self.entry_type)

        entry.options = copy.deepcopy(self.options)
        entry.params = copy.deepcopy(self.params)
        entry.func = self.func

        if not is_group:
            enable_opt = LogOption().register(
                [self.name.cmd_name],
                { "action": "store_true",
                  "help": "enable module %s" % self.name.mod_name }
            )
            entry.options.insert(0, enable_opt)

            entry.params.args = list(entry.params.args)
            entry.params.args.insert(0, self.name.mod_name)
        return entry

    def collect_group_opts(self):
        groups = {k: v.as_group_opt(is_group=True) \
            for k, v in self.groups.items() \
                if v.entry_type == EntryType.GLOBAL}
        if self.entry_type == EntryType.GLOBAL:
            groups[self.name] = self.as_group_opt()
        return groups

    def register_parser(self, *args, refs = [], **kw):
        if self.params.is_init:
            raise RuntimeError("log entry parser:" + self.name + \
                " has been registered")

        kw["refs"] = refs
        self.params.register(args, kw)
        return self

    def register_option(self, *args, **kw):
        self.options.append(LogOption().register(args, kw))
        return self

    def references(self):
        return self.params.kw.get("refs", [])

    def normalize(self):
        self.params.kw.pop("refs", [])
        if self.name in self.groups:
            del self.groups[self.name]

class LogStorage:
    STORE : Dict[LogName, LogEntry] = {}
    PARSERS = {}

    @staticmethod
    def get_entry(mod_name, entry_type) -> LogEntry:
        if isinstance(mod_name, str):
            mod_name = LogName(mod_name)

        if mod_name not in LogStorage.STORE:
            LogStorage.STORE[mod_name] = LogEntry(
                mod_name, entry_type=entry_type)
        return LogStorage.STORE[mod_name]

    @staticmethod
    def dfs_visit(entry : LogEntry, ref_path = []):
        # pruning for dfs visit
        if getattr(entry, "visited", None):
            return

        def _trigger_cycle_path(ref_name):
            common_groups = {}

            ref_path.append(ref_name)

            start = ref_path.index(ref_name)
            for ref in ref_path[start:-1]:
                ref_entry = LogStorage.STORE.get(ref, LogEntry(ref))
                # TODO: may cause undeterministic behavior, since
                #   group names may be duplicated.
                common_groups.update(ref_entry.collect_group_opts())

            for idx, ref in enumerate(ref_path[start:-1]):
                ref_entry = LogStorage.STORE.get(ref, LogEntry(ref))
                # remove dependency reference in ref_path
                ref_entry.references().remove(ref_path[start+idx+1])
                ref_entry.groups.update(common_groups)

            ref_path.pop(-1)

        ref_path.append(entry.name)

        for ref in entry.references():
            if ref in ref_path:
                _trigger_cycle_path(ref)
                continue
            ref_entry = LogStorage.get_entry(ref, EntryType.GLOBAL)
            LogStorage.dfs_visit(ref_entry, ref_path)

        # remove refs and update current entry's groups
        for ref in entry.references():
            ref_entry = LogStorage.get_entry(ref, EntryType.GLOBAL)
            entry.groups.update(ref_entry.collect_group_opts())

        setattr(entry, "visited", True)
        ref_path.remove(entry.name)

    @staticmethod
    def init_parser(parser : argparse.ArgumentParser, entry : LogEntry):
        for group in entry.groups.values():
            group.normalize()
            gparser = parser.add_argument_group(
                *group.params.args, **group.params.kw)
            for opt in group.options:
                gparser.add_argument(*opt.args, **opt.kw)

        for opt in entry.options:
            parser.add_argument(*opt.args, **opt.kw)


        def _func(args):
            is_exec = False
            for group in entry.groups.values():
                if getattr(args, group.name.arg_name, None) and \
                        group.func.is_main:
                    group.func(args)
                    is_exec = True

            if not is_exec and entry.func.is_main:
                is_exec = True
                entry.func(args)

            if not is_exec:
                raise RuntimeError(
                    "can not find module " + entry.name + \
                    " main function to run")
        parser.set_defaults(func=_func)

    @staticmethod
    def init_parser_object(parser_object, mod_name, entry):
        if "sub_parser" not in parser_object:
            parser_object["sub_parser"] = \
                parser_object["parser"].add_subparsers(
                    title = "COMMAND",
                    description = "collective sub commands")

        entry.normalize()
        mod_parser = parser_object["sub_parser"].add_parser(
            mod_name, *entry.params.args, **entry.params.kw)
        LogStorage.init_parser(mod_parser, entry)
        parser_object[mod_name] = { "parser": mod_parser, }
        return mod_parser

    @staticmethod
    def init_parsers() -> argparse.ArgumentParser:
        for entry in LogStorage.STORE.values():
            LogStorage.dfs_visit(entry)

        root_entry = LogEntry("", entry_type=EntryType.GLOBAL)
        root_entry.register_parser(
            description="bbcode helper script, implemented via python3")
        root_entry = LogStorage.STORE.get("", root_entry)

        root_entry.normalize()
        root_parser = argparse.ArgumentParser(
            *root_entry.params.args, **entry.params.kw)
        LogStorage.init_parser(root_parser, root_entry)

        # set root parser object
        LogStorage.PARSERS["parser"] = root_parser

        for entry in LogStorage.STORE.values():
            parser_object = LogStorage.PARSERS
            for mod_name, prefix in zip(
                    entry.name.mod_array, entry.name.mod_prefix_arr):
                if mod_name not in parser_object:
                    mod_entry = LogStorage.STORE.get(
                        prefix, LogEntry(prefix, EntryType.GLOBAL))
                    LogStorage.init_parser_object(
                        parser_object, mod_name, mod_entry)
                parser_object = parser_object[mod_name]
        return root_parser

    @staticmethod
    def get_parser(parser_path) -> argparse.ArgumentParser:
        parser_object = LogStorage.PARSERS
        for mod_name in LogName(parser_path).mod_array:
            if mod_name not in parser_object:
                raise RuntimeError("cannot find parser: " + parser_path)
            parser_object = parser_object[mod_name]
        return parser_object["parser"]


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
        __PARSER_KEY__: root_parser,
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
    def iterate():
        all_parsers = []
        objects = [ParserStorage.__STORES__]
        while objects:
            new_objects = []
            for parser_object in objects:
                all_parsers.append(parser_object[ParserStorage.__PARSER_KEY__])
                for k, v in parser_object.items():
                    if k in [ParserStorage.__PARSER_KEY__,
                             ParserStorage.__SUB_PARSER_KEY__,
                             ParserStorage.__GROUP_PARSER_KEY__,
                             ParserStorage.__FUNC_KEY__,]:
                        continue
                    new_objects.append(v)
            objects = new_objects
        return all_parsers

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
        mod_parser = sub_parser.add_parser(name, add_help=False, **parser_opt)
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

        # self._root_parser = root_parser
        # self._root_parser_group = None
        # self._to_main = to_main and (self._parser != self._root_parser)

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

def _path_to_parser(parser_path):
    parser_object = ParserStorage.get_parser_object(parser_path)
    return ParserStorage.get_parser_from_object(parser_object)

def _get_parser_func(parser_path, parents=[], **kw) -> ParserFunc:
    kw["parents"] = [_path_to_parser(p) for p in parents]
    parser = ParserStorage.get_parser_object(parser_path, parser_opts=[kw])
    return ParserFunc(parser)


""" CMD Revert Registration API

    Parameters
    ==========
    @param parser_path: dot splitted string, which stands for module function
    @param parents: reference module as string array
"""
# def register_option(*args, **kw):
#     def _option(pfunc : ParserFunc) -> ParserFunc:
#         pfunc.register_option(*args, **kw)
#         return pfunc
#     return _option
#
# def mod_ref(parser_path = "", **kw):
#     return _get_parser_func(parser_path, **kw).by_ref
# 
# def mod_main(parser_path = "", **kw):
#     return _get_parser_func(parser_path, **kw).by_reg
# 
# def group_ref(parser_path = "", **kw):
#     pfunc = _get_parser_func(parser_path, **kw)
#     def _ref(func):
#         return pfunc.by_group(func).by_ref(func)
#     return _ref
# 
# def group_main(parser_path = "", **kw):
#     pfunc = _get_parser_func(parser_path, **kw)
#     def _main(func):
#         return pfunc.by_group(func).by_reg(func)
#     return _main
# 
# def Run():
#     """ Main Function of Run Modules
# 
#         This function will add the help usage to all parsers.
#     """
#     for parser in ParserStorage.iterate():
#         parser.add_argument("-h", "--help", action="help",
#                             help="show this help message and exit")
# 
#     args = root_parser.parse_args()
# 
#     if getattr(args, "func", None):
#         args.func(args)
#         exit(0)
# 
#     raise RuntimeError(
#         "cannot find the mainly function to run, " +
#         "please set main function via mod_main or group_main."
#     )

def register_option(*args, **kw):
    def _func(func : LogFunction):
        func.entry.register_option(*args, **kw)
        return func
    return _func

def mod_ref(mod_name = "", entry_type = EntryType.GLOBAL):
    mod_entry = LogStorage.get_entry(mod_name, entry_type)
    mod_entry.func.is_main = False
    return mod_entry.func.wrapper

def mod_main(mod_name = "", *args, entry_type = EntryType.GLOBAL, **kw):
    mod_entry = LogStorage.get_entry(mod_name, entry_type)
    mod_entry.register_parser(*args, **kw)
    mod_entry.func.is_main = True
    return mod_entry.func.wrapper

def group_ref(mod_name = "", entry_type = EntryType.GLOBAL):
    mod_entry = LogStorage.get_entry(mod_name, entry_type)
    def _func(func):
        group_name = LogName.from_arg_name(func.__name__)
        desc = func.__doc__
        group_entry = LogEntry(group_name, entry_type)

        group_entry.func.wrapper(func)
        group_entry.func.is_main = True

        group_entry.register_parser(group_name.mod_name, description=desc)
        group_entry.func.is_main = False
        mod_entry.add_group_entry(group_entry)
        return group_entry.func
    return _func

def group_main(mod_name = "", entry_type = EntryType.GLOBAL):
    mod_entry = LogStorage.get_entry(mod_name, entry_type)
    def _func(func):
        group_name = LogName.from_arg_name(func.__name__)
        desc = func.__doc__
        group_entry = LogEntry(group_name, entry_type)

        group_entry.func.wrapper(func)
        group_entry.func.is_main = True

        group_entry.register_parser(group_name.mod_name, description=desc)
        group_entry.register_option(group_name.cmd_name,
                                    action="store_true",
                                    help="enable module " + group_name.mod_name)

        mod_entry.add_group_entry(group_entry)
        return group_entry.func
    return _func

def Run():
    root_parser = LogStorage.init_parsers()
    args = root_parser.parse_args()

    if getattr(args, "func", None):
        args.func(args)
        exit(0)

    raise RuntimeError(
        "cannot find the mainly function to run, " +
        "please set main function via mod_main or group_main."
    )

@register_option("--group-opt2", action="store_true")
@group_ref("cmd.test")
def test_group_ref(args):
    """  test group reference doc
    """
    if args.group_opt2:
        print("group opt 2")
    print("group ref")

@register_option("--group-opt1", action="store_true")
@group_main("cmd.test", entry_type=EntryType.GLOBAL)
def test_group_main(args):
    if args.group_opt1:
        print("group opt1")
    print("group main")

@register_option("--cmd-test-opt1", action="store_true", help="opt1")
@mod_ref("cmd.test")
def test_opt1(args):
    if args.cmd_test_opt1:
        print("cmd test opt1")
    print("cmd test mod ref")

@register_option("-v", "--verbosity", type=int, help="print information")
@mod_main("cmd.test", description="bbcode cmd test module")
def test_main(args):
    if args.verbosity:
        print("verbosity output")
    else:
        print("naive output")

def log_test():
    def _create_entry(name, refs = []):
        entry = LogStorage.get_entry(name)
        entry.register_parser(refs=refs)
        entry.register_option(name + "_option1", help="main option")
        entry.register_option(name + "_option2")
        entry.add_group_entry(
            LogEntry(name + "_group1")).register_option(
            "--group-opt1-" + name, help="group option " + name)
        entry.add_group_entry(
            LogEntry(name + "_group2")).register_option(
            "--group-opt2-" + name, help="group option " + name)
        entry.add_group_entry(
            LogEntry(name + "_group3", entry_type=EntryType.MODULE)).register_option(
            "--group-opt3-" + name, help="non global group option")
        print("entry info", entry.to_string())
        return entry

    ns = ["", "a", "b", "c", "d", "e"]
    e0 = _create_entry(ns[0], refs=[ns[1], ns[3]])
    e1 = _create_entry(ns[1], refs=[ns[2], ns[3]])
    e2 = _create_entry(ns[2], refs=[ns[3], ns[4]])
    e3 = _create_entry(ns[3], refs=[ns[1]])
    e4 = _create_entry(ns[4], refs=[])
    r5 = _create_entry(ns[5], refs=[])

    root_parser = LogStorage.init_parsers()
    root_parser.print_help()
    LogStorage.get_parser("a").print_help()

if __name__ == "__main__":
    @register_option("-m", "--main", action="store_true")
    @mod_main("", refs=["cmd.test"], description="bbcode main entry")
    def main(args):
        print("main")

    Run()

