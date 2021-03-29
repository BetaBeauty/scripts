from os import path

from bbcode.common import base, project, log

N2N_NAME = ".n2n"
BUILD_DIR = "build"

def download():
    url = "git@github.com:ntop/n2n.git",
    if path.exists(N2N_NAME):
        log.Print(log.DEBUG, "project", target, "already exists")
        return

    project.git_clone(
        "git@github.com:ntop/n2n.git",
        N2N_NAME,
        branch="2.8"
    )

def to_compile(is_global=False):
    with base.enter(N2N_NAME):
        base.make_dirs(BUILD_DIR)
        with base.enter(BUILD_DIR):
            CMAKE = ["cmake"]
            if is_global:
                CMAKE.append("-DCMAKE_INSTALL_PREFIX=/usr")
            CMAKE.append("..")
            base.shell_exec(CMAKE)

            MAKE = ["sudo", "make", "-j${nproc}", "install"]
            base.shell_exec(MAKE)

if __name__ == "__main__":
    download()
    to_compile(is_global=True)
