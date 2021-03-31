from os import path

from bbcode.common import base, project, log, cmd

N2N_DIR = ".tmp/n2n"
BUILD_DIR = "build"
N2N_INSTALL_DIR = "/usr"

@cmd.register_option("--n2n-dir",
                     default=N2N_DIR,
                     help="n2n download directory")
@cmd.mod_group("n2n")
def download(args):
    url = "git@github.com:ntop/n2n.git",
    if path.exists(args.n2n_dir):
        log.Print(log.DEBUG, "project", args.n2n_dir, "already exists")
        return

    project.git_clone(
        "git@github.com:ntop/n2n.git",
        N2N_DIR,
        branch="2.8"
    )

@cmd.register_option("--install-dir",
                     default=N2N_INSTALL_DIR,
                     help="the global path to be installed for n2n" +
                        ", if the compile global is set")
@cmd.register_option("--compile-global",
                     action="store_true",
                     help="whether to compile to system global path")
@cmd.mod_group("n2n")
def to_compile(args):
    with base.enter(N2N_DIR):
        base.make_dirs(BUILD_DIR)
        with base.enter(BUILD_DIR):
            CMAKE = ["cmake"]
            if args.compile_global:
                CMAKE.append("-DCMAKE_INSTALL_PREFIX=" + args.install_dir)
            CMAKE.append("..")
            base.shell_exec(CMAKE)

            MAKE = []
            if args.compile_global:
                MAKE.appen("sudo")
            MAKE.extend(["make", "-j${nproc}"])
            if args.compile_global:
                MAKE.append("install")
            base.shell_exec(MAKE)

if __name__ == "__main__":
    args = cmd.parse_args()

    download(args)
    to_compile(args)
