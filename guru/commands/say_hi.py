from guru.commands.convert_to_cmake import replace_necessary_code_line

COMMAND_NAME = "hi"


def active_command(parameters):
    """
    Responsible to extract all the necessary properties and active
    the right command.
    :param parameters: The params from the user (expect to a list like that: []).
    """
    print("""
      _____
    _/ ____\  ____  
    \   __\  / __ \ 
     |  |    \  __/ 
     |__|     \____|
        """)
    print("Hi back...")
