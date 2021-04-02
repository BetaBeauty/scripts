from bbcode.common import cmd, log

@cmd.mod_main("", parents=["log", "cmd"])
def main(args):
    print(args)

if __name__ == "__main__":
    cmd.Run()
