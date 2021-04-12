from bbcode.common import cmd

N2N_NAME = "n2n"
BUILD_DIR = "build"

@cmd.option("--system", action="store_true",
            help="whether to compile/run via global system path")
@cmd.module("n2n.common")
def n2n_common(args):
    pass
