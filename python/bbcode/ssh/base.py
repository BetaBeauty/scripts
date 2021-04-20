from os import path

DEFAULT_SSH_DIRECTORY = path.expanduser("~/.ssh")

def parse_user(server):
    args = ([None] + server.split("@"))[-2:]
    return args[0], args[1]

def parse_url(server, default_port):
    args = (server.split(":", 1) + [default_port])[:2]
    args[1] = int(args[1])
    args[0] = args[0].replace("*", "0.0.0.0")
    return args[0], args[1]
