import os
import logging
import subprocess

bash_logger = logging.getLogger("bash")

def make_dirs(dir_path):
    os.makedirs(dir_path, exist_ok=True)

def shell_exec(*commands, check_error=False):
    str_com = " ".join([str(c) for c in commands])
    bash_logger.debug(str_com)
    code = os.system(str_com)
    if check_error and (code != 0):
        raise RuntimeError(
            "command execute terminated: {}".format(str_com))
    return code

def sub_command(*commands, check_error=False):
    split_coms = []
    for com in commands:
        split_coms.extend(com.split())
    proc = subprocess.run(split_coms, shell=True, stdout=subprocess.PIPE)
    if check_error and proc.returncode != 0:
        raise RuntimeError(
            "command execute terminated: {}".format(split_coms))
    return proc.stdout


class DirEntry:
    def __init__(self, target_dir):
        self._curr_dir = os.getcwd()
        self._tar_dir = target_dir

    def __enter__(self):
        bash_logger.debug("cd {}".format(self._tar_dir))
        os.chdir(self._tar_dir)

    def __exit__(self, *args):
        bash_logger.debug("cd {}".format(self._curr_dir))
        os.chdir(self._curr_dir)

# using with python `with` primitive enter block
def enter(target_dir, create=False):
    if create:
        make_dirs(target_dir)
    return DirEntry(target_dir)

def singleton(cls):
    instances = {}
    def _singleton(*args, **kw):
       if cls not in instances:
            instances[cls] = cls(*args, **kw)
       return instances[cls]
    return _singleton

def validate(cond, msg):
    if not cond:
        raise RuntimeError(msg)
