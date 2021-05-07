import os
from os import path
import json
import ycm_core

class CPPFindor:
    def __init__(self, root):
        self._root = root
        self.common_flags = []
        self.flags = {}

    def find(self):
        return self._find_cmake_flags()

    def _find_sys_lib(self, binary):
        version = '11.0'
        flag = "-I/usr/include/c++/%s" % version
        if flag not in self.common_flags:
            self.common_flags.append(flag)

    def _find_c_flags(self, options):
        CXX_KEYS = ['-I', '-W', '-D', '-m', '-s', '-f']
        for opt in options:
            if opt[:2] in CXX_KEYS and opt not in self.common_flags:
                self.common_flags.append(opt)

    def _find_cmake_flags(self):
        db_fname = 'compile_commands.json'
        db_fpath = path.join(self._root, db_fname)

        if not path.exists(db_fpath):
            return False

        with open(db_fpath, "r") as fin:
            commands = json.load(fin)

        CMAKE_COM_KEY = 'command'
        for com in commands:
            if CMAKE_COM_KEY in com:
                com = com[CMAKE_COM_KEY]
                com = [x for x in com.split(' ') if x]
                # self.common_flags = self._find_sys_lib(com[0])
                self._find_c_flags(com)

        return True

def is_git_project(file_path):
    " Naive check the `.git` directory, may be use gitpython package. "
    return path.exists(path.join(file_path, ".git"))

def try_find_cmake_exports(flags):
    work_directory = os.getcwd()
    while work_directory != "/":
        walk_dirs = [
            work_directory,
            path.join(work_directory, "build"),
        ]

        for p in walk_dirs:
            findor = CPPFindor(p)
            if findor.find():
                flags.extend(findor.common_flags)
                return

        if is_git_project(work_directory):
            return

        walk_dirs = path.dirname(walk_dirs)

SRC_LANG = {
    'cuda': ['.cuh', '.cu'],
    'c++': ['.c', '.cc', '.cxx', '.cpp', '.h', '.hpp', '.hxx', 'hh']
}

def GCC_BIN(flags, binary):
    with os.popen(binary + " -dumpversion") as f:
        version = f.readline().strip()

    LIB_PATH = "/usr/include/c++/%s" % version
    flag = "-I%s" % LIB_PATH
    if os.path.exists(LIB_PATH) and flag not in flags:
        flags.append(flag)
    return flags

def SourceLangFlags(flags, filename):
    ext = os.path.splitext(filename)[-1]
    for lang, suffixs in SRC_LANG.items():
        if ext in suffixs and lang not in flags:
            flags.extend(['-x', lang])
    return flags

C_VERSION = '11'
COMMON_FLAGS = [ '-I/usr/lib/', '-I/usr/include/', '-std=c++%s' % C_VERSION ]
GCC_BIN(COMMON_FLAGS, 'g++')
try_find_cmake_exports(COMMON_FLAGS)

def Settings(**kwargs):
    filename = kwargs['filename']
    if kwargs['language'] != 'cfamily':
        return {}

    final_flags = COMMON_FLAGS[:]
    final_flags = SourceLangFlags(final_flags, filename)

    return {
      'flags': final_flags,
    }
