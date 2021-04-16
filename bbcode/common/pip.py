from . import base, cmd

def pip_install(*names, pip_path="pip"):
    for n in names:
        base.shell_exec(
            pip_path,
            "install",
            n,
            check_error=True)
