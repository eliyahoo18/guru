import enum
import os
import os.path
import typer

from termcolor import colored


class Action(enum.Enum):
    System = 0
    Fine = 1
    Bad = 2
    Modify = 3
    Error = 4


reports = {
    Action.System: ("@", None),
    Action.Fine: ("+", 'green'),
    Action.Bad: ("-", 'red'),
    Action.Modify: ("~", 'yellow'),
    Action.Error: ("∆", 'red'),
}


def sys_report(msg, action):
    print(f"::guru @ {colored(msg, reports[action][1])}")


def report(msg, action):
    print(colored(f'{reports[action][0]} {msg}', reports[action][1]))


def report_on_file(path, action):
    relativePath = os.path.relpath(path, os.getcwd())
    print(colored(f"::guru {reports[action][0]} {relativePath}", reports[action][1]))
