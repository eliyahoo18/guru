import guru.commands.say_hi
import guru.commands.convert_to_cmake
import guru.commands.chage_app_theme
import guru.commands.process_bot
import guru.logger


# Chose the command' and execute it


def commands(command, parameters):
    # Say Hi!
    if command == guru.commands.say_hi.COMMAND_NAME:
        guru.commands.say_hi.active_command(parameters)

    # Convert any cpp project to cmake project
    elif command == guru.commands.convert_to_cmake.COMMAND_NAME:
        guru.commands.convert_to_cmake.active_command(parameters)

    # Turn off the default theme for specific app.
    elif command == guru.commands.chage_app_theme.COMMAND_NAME:
        guru.commands.chage_app_theme.active_command(parameters)

    #
    elif command == guru.commands.process_bot.COMMAND_NAME:
        guru.commands.process_bot.active_command(parameters)

    # Default case...
    else:
        guru.logger.report(f"The command \"{command}\" not found", 'red')
