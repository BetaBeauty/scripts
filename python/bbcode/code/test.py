
from bbcode.common import base, cmd

from . import create

@cmd.option("-r", "--run",
            help="run test, depends on compile")
@cmd.option("-c", "--compile",
            help="compile test")
@cmd.module("code.test", as_main=True,
            refs=["code.init"],
            help="code test tool",
            description="create cpp tests")
def init_test_code(args):
    args.root =  args.root or path.join(base.BBCODE_ROOT, "cpp/tests")
    create.init_code(args)
