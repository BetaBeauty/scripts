from typing import List

class Command:
    def __init__(self, command_name : str):
        self._command = [command_name]

    def sub_command(self, sub_name : str):
        self._command.append(sub_name)

    def option(self, option : str):
        self._command.append(option)
