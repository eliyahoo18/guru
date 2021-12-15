import enum
import os
import os.path

from termcolor import colored


class Action(enum.Enum):
   Add = 1
   Remove = 2
   Modify = 3
   Error = 4


def report_on_file(path, action):
   relativePath = os.path.relpath(path, os.getcwd())
   report = {
      Action.Add: ("+", 'green'),
      Action.Remove: ("-", 'red'),
      Action.Modify: ("~", 'yellow'),
   }[action]
   print(colored(f"{report[0]} {relativePath}", report[1]))
