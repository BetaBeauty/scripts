""" Code Core Submodule Initialization Main
"""
import os
from os import path

from bbcode.common import base, cmd

class SafeDict(dict):
    def __missing__(self, key):
        return "{"+ key + "}"

MAKEFILE = """
.PHONY: all compile run prepare clean

BUILD := build
INCLUDE := {link_path}/include
BIN := bin
SRCS := $(wildcard *.cpp) $(wildcard *.c)

all: prepare compile run

compile: ${SRCS}
\t@echo "Compile into ${BUILD}/${BIN}..."
\tg++ -o ${BUILD}/${BIN} $< -std=c++11 -I${INCLUDE} -g -Wall

run: compile
\t@echo "Run with ${BUILD}/${BIN}..."
\t@${BUILD}/${BIN}

gdb:
\tgdb --args ${BUILD}/${BIN}

prepare:
\t@mkdir -p ${BUILD}

clean:
\trm -rf ${BUILD}/${BIN}
"""

MAIN_CODE = """
#include <iostream>
#include <cstring>

int main(int argc, char **argv) {
  return 0;
}
"""

@cmd.option("--root", default=None,
            help=" ".join([
                "code project base root directory,",
                "working directory by default"
            ]))
@cmd.option("name",
            help="project name, and create sub directory")
@cmd.module("code.init", as_main=True)
def init_code(args):
    code_root = args.root or os.getcwd()
    code_path = path.join(code_root, args.name)

    code_core = path.join(base.BBCODE_ROOT, "cpp")
    core_relative_path = path.relpath(code_core, start=code_path)

    with base.enter(code_path, create=True):
        with open(path.join(code_path, "main.cpp"), "w") as f:
            f.write(MAIN_CODE)

        with open(path.join(code_path, "Makefile"), "w") as f:
            f.write(MAKEFILE.format_map(SafeDict(
                link_path=core_relative_path)))
