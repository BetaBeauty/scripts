import os
import json
import ycm_core

BUILD_DIRECTORY = 'build'
SRC_LANG = {
    'cuda': ['.cuh', '.cu'],
    'c++': ['.c', '.cc', '.cxx', '.cpp', '.h', '.hpp', '.hxx', 'hh']
}

def GCC_BIN(flags, binary):
    with os.popen(binary + " -dumpversion") as f:
        version = f.readline().strip()

    flag = "-I/usr/include/c++/" + version
    if flag not in flags:
        flags.append(flag)
    return flags


def SourceLangFlags(flags, filename):
    ext = os.path.splitext(filename)[-1]
    for lang, suffixs in SRC_LANG.items():
        if ext in suffixs and lang not in flags:
            flags.extend(['-x', lang])
    return flags

def DirectoryOfThisScript():
  return os.path.dirname(os.path.abspath(__file__))

COMMON_FLAGS = [
    '-I/usr/lib/',
    '-I/usr/include/',
    '-Wall',
    '-std=c++11',
    '-I%s/cpp/include' % DirectoryOfThisScript(),
]
GCC_BIN(COMMON_FLAGS, 'g++')

def Settings(**kwargs):
    filename = kwargs['filename']
    if kwargs['language'] != 'cfamily':
        return {}

    final_flags = COMMON_FLAGS[:]
    final_flags = SourceLangFlags(final_flags, filename)

    return {
      'flags': final_flags,
    }
