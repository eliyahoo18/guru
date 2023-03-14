import sys
import guru.logger
import guru.command

from guru.logger import Action


def main():
    guru.logger.sys_report("activated", Action.Fine)

    # try:
    # Gets the command fields
    args = sys.argv[1:]
    if not args:
        raise Exception("What to do?")

    # Search the command
    guru.command.commands(args[0], args[1:])

    # except Exception as e:
    #     guru.logger.report(f"{e}", Action.Error)

    guru.logger.sys_report("deactivated", Action.Fine)


if __name__ == '__main__':
    main()
