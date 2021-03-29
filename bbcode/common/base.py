import os

from . import log

def make_dirs(dir_path):
    os.makedirs(dir_path, exist_ok=True)

def shell_exec(command, check_error=False):
    log.Print(log.COMMAND, *command)
    code = os.system(" ".join(command))
    if check_error and (code != 0):
        raise RuntimeError("command execute terminated")
    return code

class DirEntry:
    def __init__(self, target_dir):
        self._curr_dir = os.getcwd()
        self._tar_dir = target_dir

    def __enter__(self):
        log.Print(log.COMMAND, "cd", self._tar_dir)
        os.chdir(self._tar_dir)

    def __exit__(self, *args):
        log.Print(log.COMMAND, "cd", self._curr_dir)
        os.chdir(self._curr_dir)

# using with python `with` primitive enter block
def enter(target_dir, condition=True):
    if condition:
        return DirEntry(target_dir)
    return object()

def singleton(cls):
    instances = {}
    def _singleton(*args, **kw):
       if cls not in instances:
            instances[cls] = cls(*args, **kw)
       return instances[cls]
    return _singleton
