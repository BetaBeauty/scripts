from __future__ import annotations

import os
from os import path
import platform
import json

from typing import Dict, Sequence, Tuple, List, Callable

class OS:
    Linux = 'Linux'
    MacOS = 'Darwin'

# custom type
Flags = List[str]
Params = Dict[str, str]
FlagerFunc = Callable[[Flags, Params], bool]


class PackedFunc:
    def __init__(self, func, deps):
        self._func = func
        self._deps = deps

    @property
    def name(self):
        return self._func.__name__

    def __call__(self, flags : Flags, params : Params) -> bool:
        for dep in self._deps:
            if dep not in params:
                print("[ERROR]: function:<{}> dependency:{} is not satified.".format(
                    self._func.__name__, dep))
                return False
        ret = self._func(flags, params)
        ret = True if ret is None else ret # process default none return
        return ret

__OS_TYPE__ = platform.system()
__SUPPORTED_OS__ = [OS.Linux, OS.MacOS]
assert __OS_TYPE__ in __SUPPORTED_OS__, "can not find correleated OS: %s" % os_type


class FlagerFactory:
    __INSTANCES__ = {}

    def __init__(self):
        self._flagers : List[PackedFunc] = []

    @classmethod
    def __GLOBAL__(cls) -> FlagerFactory:
        if cls not in cls.__INSTANCES__:
            cls.__INSTANCES__[cls] = cls()
        return cls.__INSTANCES__[cls]

    @classmethod
    def parse(cls, flags : Flags, params : Params):
        cls.__GLOBAL__().generate_flags(flags, params)

    @classmethod
    def register_flager(cls,
                        deps : List[str] = [],
                        os_type : List[str] = __SUPPORTED_OS__):
        def flager(flager : FlagerFunc):
            if __OS_TYPE__ not in os_type:
                return
            cls.__GLOBAL__()._flagers.append(PackedFunc(flager, deps))
        return flager

    def generate_flags(self, flags : Flags, params : Params):
        assert False, "to be implemented in derived class"


class CFamilyFlager(FlagerFactory):
    __LANG__ = "cfamily"

    def generate_flags(self, flags : Flags, params : Params):
        if params.get("language", "") != self.__LANG__:
            return
        return self._cxx_generate_flags(flags, params)

    def _cxx_generate_flags(self, flags : Flags, params : Params):
        assert False, "to be implemented in derived class"


class CCommonFlager(CFamilyFlager):
    def _cxx_generate_flags(self, flags : Flags, params : Params):
        for flager in self._flagers:
            is_ok = flager(flags, params)
            if not is_ok:
                print("[Error]: function:{} parsed failed".format(flager.name))
        return True


class CTrivalFlager(CFamilyFlager):
    def _cxx_generate_flags(self, flags : Flags, params : Params):
        is_race = False
        for flager in self._flagers:
            is_race = flager(flags, params)
            if is_race:
                return True
        print("[Warning]: all cxx generate flagers failed")
        return False


class CPatchFlager(CCommonFlager):
    pass

# =================== Common API for Ycm Core ====================

def generate_flags(params):
    flags = []
    CCommonFlager.parse(flags, params)
    CTrivalFlager.parse(flags, params)
    CPatchFlager.parse(flags, params)
    return flags

# ===================== Compilation Module =======================


class CompilationBinaryFlager:
    """ TODO: add support for clang binary
    """
    __SUPPORTED_BINS__ = ["gcc", "g++", "cc", "c++"]

    @staticmethod
    @CPatchFlager.register_flager(deps=["compile_binary"], os_type=[OS.Linux])
    def FindCompilationLibrary(flags : Flags, params : Params):
        compile_binary = params.get("compile_binary")
        is_supported = False
        for bin_name in CompilationBinaryFlager.__SUPPORTED_BINS__:
            if bin_name in compile_binary:
                is_supported = True

        if not is_supported:
            return True

        with os.popen(compile_binary + " -dumpversion") as f:
            version = f.readline().strip()

        flag = "-I/usr/include/c++/%s" % version
        flags.append(flag)


class CxxLangFlager:
    __SRC_LANGS__ = {
        "cuda": [".cuh", ".cu"],
        "c++": [".cxx", ".cpp", ".h", ".hpp", ".hxx", ".hh", ".tcc"],
        "c": [".c", ".cc"],
    }

    @staticmethod
    @CPatchFlager.register_flager(deps=["filename"])
    def FindLangFlags(flags : Flags, params : Params):
        if "-x" in flags:
            return True

        filename = params.get("filename")
        ext = os.path.splitext(filename)[-1]
        for lang, suffixs in CxxLangFlager.__SRC_LANGS__.items():
            if ext in suffixs:
                flags.extend(["-x", lang])

@CCommonFlager.register_flager()
def CommonFlags(flags : Flags, params : Params):
    flags.extend(["-I/usr/lib", "-I/usr/include"])


class CMakeFlager:
    """ TODO: store the map for different source file with different cxx flags,
            instead of reflatten into the same collection.
    """
    DB_FNAME = "compile_commands.json"
    __INSTANCES__ : Dict[str, CMakeFlager] = {}

    def __init__(self, root):
        self._root = root
        self._flags = None
        self._binary = None

    @staticmethod
    def _trival_find_root(root):
        while root != "/":
            walk_dirs = [root, path.join(root, "build")]
            for d in walk_dirs:
                if path.exists(path.join(d, CMakeFlager.DB_FNAME)):
                    return d

            root = path.dirname(root)
        return root

    @staticmethod
    @CTrivalFlager.register_flager(deps=["filename"])
    def FindCMakeFlags(flags : Flags, params : Params):
        filename = params.get("filename")
        root = path.dirname(path.realpath(filename))
        root = CMakeFlager._trival_find_root(root)

        if CMakeFlager.__INSTANCES__.get(root, None) is None:
            CMakeFlager.__INSTANCES__[root] = CMakeFlager(root)
        return CMakeFlager.__INSTANCES__[root]._generate_flags(flags, params)

    def _generate_flags(self, flags : Flags, params : Params):
        # Cannot find the cmake project root, return False to give up race.
        if self._root == "/":
            return False

        # Cxx flags cache.
        if self._flags is None:
            self._flags = self._parse_cmake(path.join(self._root, self.DB_FNAME))

        self._set_prequisties_for_binary(params)

        # Since all the flags are the single primitive without whitespace,
        #   we simply check the duplicate key to append the cxx flags.
        flags.extend([f for f in self._flags if f not in flags])
        return True

    def _parse_cxx_flags(self, options):
        keys = ['-I', '-W', '-D', '-m', '-s', '-f']
        return [opt for opt in options if opt[:2] in keys]

    def _parse_cmake(self, db_fpath):
        with open(db_fpath, "r") as fin:
            commands = json.load(fin)

        flags = []
        com_key = "command"
        self._binary = None # update the binary parser
        for com in commands:
            com = com.get(com_key, "")
            com_arr = [x for x in com.split(' ') if x]
            if self._binary is None and len(com_arr) > 0:
                self._binary = com_arr[0]
            parsed_flags = self._parse_cxx_flags(com_arr)
            for flag in parsed_flags:
                if flag not in flags:
                    flags.append(flag)
        return flags

    def _set_prequisties_for_binary(self, params : Params):
        if self._binary is not None:
            params["compile_binary"] = self._binary

@CPatchFlager.register_flager()
def TrivalFixFlags(flags : Flags, params : Params):
    for flag in flags:
        if flag.startswith('-std='):
            return True
    flags.append("-std=c++11")

def Settings(**kwargs):
    flags = generate_flags(kwargs)
    return { 'flags': flags, }

if __name__ == "__main__":
    filename = "/home/serving/zion/3rd_party/loopring/protocols/packages/loopring_v3/circuit/main.cpp"
    params = {
        "filename": filename,
        "language": "python",
    }
    print("First set", Settings(**params))
    print("Second set", Settings(**params))

    # conf = Preference.Global(filename=filename)
    # conf.analysis_curr_project() # do once
    # flags = conf.generate_flags()
    # print (flags)
