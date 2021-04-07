from __future__ import annotations

from typing import Sequence, Dict
from typing import Callable

import copy
from enum import Enum

import argparse

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

class CmdName:
    """ Formatted Cmder Name

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

    def __eq__(self, other : CmdName):
        if isinstance(other, str):
            other = CmdName(other)
        return other.name == self.name

    @staticmethod
    def from_mod_array(mod_arr : Sequence[str]) -> CmdName:
        return CmdName(".".join(mod_arr))

    @staticmethod
    def from_cmd_name(cmd_name : str) -> CmdName:
        return CmdName(cmd_name.replace("-", "."))

    @staticmethod
    def from_arg_name(arg_name : str) -> CmdName:
        return CmdName(arg_name.replace("_", "."))

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

class CmdOption:
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

class CmdFunction:
    def __init__(self, entry):
        self.entry : CmdEntry = entry
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

class CmdEntry:
    def __init__(self, name : CmdName, entry_type : EntryType):
        self.name : CmdName = name
        self.entry_type = entry_type
        self.options : Sequence[CmdOption] = []
        self.params : CmdOption = CmdOption()
        self.func : CmdFunction = CmdFunction(self)
        self.groups : Dict[CmdName, CmdEntry] = {}

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

    def add_group_entry(self, entry) -> CmdEntry:
        if entry.name in self.groups:
            raise RuntimeError("group " + entry.name + " has been registered")
        self.groups[entry.name] = entry
        return self.groups[entry.name]

    def as_group_opt(self, is_group=False):
        entry = CmdEntry(self.name, entry_type=self.entry_type)

        entry.options = copy.deepcopy(self.options)
        entry.params = copy.deepcopy(self.params)
        entry.func = self.func

        if not is_group:
            enable_opt = CmdOption().register(
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
        self.options.append(CmdOption().register(args, kw))
        return self

    def references(self):
        return self.params.kw.get("refs", [])

    def normalize(self):
        self.params.kw.pop("refs", [])
        if self.name in self.groups:
            del self.groups[self.name]

class CmdStorage:
    STORE : Dict[CmdName, CmdEntry] = {}
    PARSERS = {}

    @staticmethod
    def get_entry(mod_name, entry_type) -> CmdEntry:
        if isinstance(mod_name, str):
            mod_name = CmdName(mod_name)

        if mod_name not in CmdStorage.STORE:
            CmdStorage.STORE[mod_name] = CmdEntry(
                mod_name, entry_type=entry_type)
        return CmdStorage.STORE[mod_name]

    @staticmethod
    def dfs_visit(entry : CmdEntry, ref_path = []):
        # pruning for dfs visit
        if getattr(entry, "visited", None):
            return

        def _trigger_cycle_path(ref_name):
            common_groups = {}

            ref_path.append(ref_name)

            start = ref_path.index(ref_name)
            for ref in ref_path[start:-1]:
                ref_entry = CmdStorage.STORE.get(ref, CmdEntry(ref))
                # TODO: may cause undeterministic behavior, since
                #   group names may be duplicated.
                common_groups.update(ref_entry.collect_group_opts())

            for idx, ref in enumerate(ref_path[start:-1]):
                ref_entry = CmdStorage.STORE.get(ref, CmdEntry(ref))
                # remove dependency reference in ref_path
                ref_entry.references().remove(ref_path[start+idx+1])
                ref_entry.groups.update(common_groups)

            ref_path.pop(-1)

        ref_path.append(entry.name)

        for ref in entry.references():
            if ref in ref_path:
                _trigger_cycle_path(ref)
                continue
            ref_entry = CmdStorage.get_entry(ref, EntryType.GLOBAL)
            CmdStorage.dfs_visit(ref_entry, ref_path)

        # remove refs and update current entry's groups
        for ref in entry.references():
            ref_entry = CmdStorage.get_entry(ref, EntryType.GLOBAL)
            entry.groups.update(ref_entry.collect_group_opts())

        setattr(entry, "visited", True)
        ref_path.remove(entry.name)

    @staticmethod
    def init_parser(parser : argparse.ArgumentParser, entry : CmdEntry):
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
        CmdStorage.init_parser(mod_parser, entry)
        parser_object[mod_name] = { "parser": mod_parser, }
        return mod_parser

    @staticmethod
    def init_parsers() -> argparse.ArgumentParser:
        for entry in CmdStorage.STORE.values():
            CmdStorage.dfs_visit(entry)

        root_entry = CmdEntry("", entry_type=EntryType.GLOBAL)
        root_entry.register_parser(
            description="bbcode helper script, implemented via python3")
        root_entry = CmdStorage.STORE.get("", root_entry)

        root_entry.normalize()
        root_parser = argparse.ArgumentParser(
            *root_entry.params.args, **root_entry.params.kw)
        CmdStorage.init_parser(root_parser, root_entry)

        # set root parser object
        CmdStorage.PARSERS["parser"] = root_parser

        for entry in CmdStorage.STORE.values():
            parser_object = CmdStorage.PARSERS
            for mod_name, prefix in zip(
                    entry.name.mod_array, entry.name.mod_prefix_arr):
                if mod_name not in parser_object:
                    mod_entry = CmdStorage.STORE.get(
                        prefix, CmdEntry(prefix, EntryType.GLOBAL))
                    CmdStorage.init_parser_object(
                        parser_object, mod_name, mod_entry)
                parser_object = parser_object[mod_name]
        return root_parser

    @staticmethod
    def get_parser(parser_path) -> argparse.ArgumentParser:
        parser_object = CmdStorage.PARSERS
        for mod_name in CmdName(parser_path).mod_array:
            if mod_name not in parser_object:
                raise RuntimeError("cannot find parser: " + parser_path)
            parser_object = parser_object[mod_name]
        return parser_object["parser"]


""" CMD Registration API
"""

def register_option(*args, **kw):
    def _func(func : CmdFunction):
        func.entry.register_option(*args, **kw)
        return func
    return _func

def mod_ref(mod_name = "", entry_type = EntryType.GLOBAL):
    mod_entry = CmdStorage.get_entry(mod_name, entry_type)
    mod_entry.func.is_main = False
    return mod_entry.func.wrapper

def mod_main(mod_name = "", *args, entry_type = EntryType.GLOBAL, **kw):
    mod_entry = CmdStorage.get_entry(mod_name, entry_type)
    mod_entry.register_parser(*args, **kw)
    mod_entry.func.is_main = True
    return mod_entry.func.wrapper

def group_ref(mod_name = "", entry_type = EntryType.GLOBAL):
    mod_entry = CmdStorage.get_entry(mod_name, entry_type)
    def _func(func):
        group_name = CmdName.from_arg_name(func.__name__)
        desc = func.__doc__
        group_entry = CmdEntry(group_name, entry_type)

        group_entry.func.wrapper(func)
        group_entry.func.is_main = True

        group_entry.register_parser(group_name.mod_name, description=desc)
        group_entry.func.is_main = False
        mod_entry.add_group_entry(group_entry)
        return group_entry.func
    return _func

def group_main(mod_name = "", entry_type = EntryType.GLOBAL):
    mod_entry = CmdStorage.get_entry(mod_name, entry_type)
    def _func(func):
        group_name = CmdName.from_arg_name(func.__name__)
        desc = func.__doc__
        group_entry = CmdEntry(group_name, entry_type)

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
    root_parser = CmdStorage.init_parsers()
    args = root_parser.parse_args()

    if getattr(args, "func", None):
        args.func(args)
        exit(0)

    raise RuntimeError(
        "cannot find the mainly function to run, " +
        "please set main function via mod_main or group_main."
    )

""" CMD Test Code and Command Line
"""
def register_test_func():
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

if __name__ == "__main__":
    register_test_func()

    @register_option("-m", "--main", action="store_true")
    @mod_main("", refs=["cmd.test"], description="bbcode main entry")
    def main(args):
        print("main")

    Run()

