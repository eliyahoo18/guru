import os

COMMAND_NAME = "-ddtheme"  # -> "disable-default-theme"
APP_NAME = 0
TURN_OFF = 1


def get_bundle_identifier(app_name):
    """
    :return: The app bundle identifier.
    """
    bundle_identifier = os.popen(f"osascript -e 'id of app \"{app_name}\"'").read().strip()
    print(bundle_identifier)
    return bundle_identifier


def disable_app_default_theme(bundle_identifier):
    """
    Disable the default theme for specific app.
    :param bundle_identifier: the app bundle identifier (use 'get_bundle_identifier'
                              to get the app bundle identifier).
    """
    print(os.popen(f"defaults write {bundle_identifier} NSRequiresAquaSystemAppearance -bool yes").read())


def enable_app_default_theme(bundle_identifier):
    """
    Removes the 'disable_app_default_theme' command form the system, this mean
    that this app return to shown as the default theme.
    :param bundle_identifier: the app bundle identifier (use 'get_bundle_identifier'
                              to get the app bundle identifier).
    """
    print(os.popen(f"defaults delete {bundle_identifier} NSRequiresAquaSystemAppearance").read())


def turn_off_default_theme(app_name):
    """
    Turn off the default theme for specific app.
    :param app_name: the app name.
    """
    bundle_identifier = get_bundle_identifier(app_name)
    disable_app_default_theme(bundle_identifier)


def turn_back_on_default_theme(app_name):
    """
    Turn back on the default theme for specific app.
    :param app_name: the app name.
    """
    bundle_identifier = get_bundle_identifier(app_name)
    enable_app_default_theme(bundle_identifier)


def active_command(parameters):
    """
    Responsible to extract all the necessary properties and active
    the right command.
    :param parameters: The params from the user (expect to a list like that: [<app-name>,<to-turn-off=True>]).
    """
    if not parameters:
        print("missing <app name>.")
        return

    app_name = parameters[APP_NAME]
    # set a default value, if the user did not specify one
    turn_off = True if len(parameters) < 2 else (parameters[TURN_OFF].lower() == "true")

    if turn_off:
        turn_off_default_theme(app_name)
    else:
        turn_back_on_default_theme(app_name)
