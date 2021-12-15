import sys

from termcolor import colored
from guru.command import commands


def main():
    # Gets the command fields
    args = sys.argv[1:]
    if not args:
        print(colored("What to do?", 'red'))
        return

    try:
        # Search the command
        commands(args[0], args[1:])

    except Exception as e:
        print(colored(f"{e}\n\n", 'red'))


if __name__ == '__main__':
    main()
