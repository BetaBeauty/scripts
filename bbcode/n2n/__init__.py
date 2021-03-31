from bbcode.common import cmd

from .code import download, to_compile

cmd.mod_parser("n2n", help="Project N2N Module")

if __name__ == "__main__":
    args = cmd.parse_args()
