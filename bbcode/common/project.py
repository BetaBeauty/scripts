from . import base

def git_clone(url, target_dir,
        is_recursive=True, branch=None):
    command = ["git", "clone"]
    if is_recursive:
        command.append("--recurse-submodules")
    command.append(url)
    command.append(target_dir)
    base.shell_exec(command, check_error=True)

    with base.enter(target_dir, condition=branch):
        command = ["git", "checkout", branch]
        base.shell_exec(command, check_error=True)

if __name__ == "__main__":
    git_clone("git@github.com:BetaBeauty/code_core.git", "test", branch="wlt")
