import fcntl
import os
import subprocess
import time
import re

from termcolor import colored

COMMAND_NAME = "-pb"  # -> "process bot"
PROCESS_NAME = 0
INSTRUCTION_FILE_PATH = 1
READ_FIRST_FLAG = ">>"
TEST_MODE_FLAG = "(!)"
HELP = \
    '''
    The instruction file syntax:
    
    [first-line]
        << - write the command and then read from the process.
        >> - read from the process and then write the command.
        (!) - for testing the process, need do get also the correct response of the process.     
    [other-line]
        1 - """the line to write to the process."""
        # 2 (!) - """the right response from the process. (necessary just if the execution mark as test)"""
        # .
        .
        .
'''
PASS = \
    '''
                                  _   
     _ __   __ _ ___ ___  ___  __| |  
    | '_ \ / _` / __/ __|/ _ \/ _` |  
    | |_) | (_| \__ \__ \  __/ (_| |_ 
    | .__/ \__,_|___/___/\___|\__,_(_)
    |_|                                            
'''
FAILED = \
    '''
      █████▒▄▄▄       ██▓ ██▓    ▓█████ ▓█████▄ 
    ▓██   ▒▒████▄    ▓██▒▓██▒    ▓█   ▀ ▒██▀ ██▌
    ▒████ ░▒██  ▀█▄  ▒██▒▒██░    ▒███   ░██   █▌
    ░▓█▒  ░░██▄▄▄▄██ ░██░▒██░    ▒▓█  ▄ ░▓█▄   ▌
    ░▒█░    ▓█   ▓██▒░██░░██████▒░▒████▒░▒████▓ 
     ▒ ░    ▒▒   ▓▒█░░▓  ░ ▒░▓  ░░░ ▒░ ░ ▒▒▓  ▒ 
     ░       ▒   ▒▒ ░ ▒ ░░ ░ ▒  ░ ░ ░  ░ ░ ▒  ▒ 
     ░ ░     ░   ▒    ▒ ░  ░ ░      ░    ░ ░  ░ 
                 ░  ░ ░      ░  ░   ░  ░   ░    
                                         ░                      
'''


def communicate_with_process(process_name, instructions_file_path):
    """
    Run a process with geven input. the geven input came in the instruction
    file. Its print all the output of the process but not the input that
    given to the process.
    """
    # open the process with write and read option actives.
    process = subprocess.Popen(process_name,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               # and for unlimited buffer size
                               bufsize=0)

    # open and read all the instructions file in once
    head_line, instructions = read_instructions_file(instructions_file_path)
    read_first, in_test_mode = parse_head_line(head_line)

    test_passed = test_process_flow(process, instructions, read_first, in_test_mode)
    if in_test_mode:
        if test_passed:
            print(colored(PASS, "green"))
        else:
            print(colored(FAILED, "red"))


def test_process_flow(process, instructions, read_first, in_test_mode):
    """
    Communicate with the process by write and read the command followed by
    the instructions list. if the test flag is on - its check also if the output of
    the process if the exactly like the instructions.
    If so return True, otherwise return False.
    """

    # read chuck of data before get into the loop and start write back to the process
    if read_first:
        output = read_chunk_from_process(process)
        if in_test_mode:
            # check that the process response how we expect
            if not confirms_output(output, instructions[0]):
                return False
            instructions.pop(0)
        else:
            print(output)

    i = 0
    while i < len(instructions):
        write_line = instructions[i]

        # write the command to the process and print its in green
        process.stdin.write(bytes(write_line + "\n", "ascii"))

        if in_test_mode:
            # end of file...
            if (i + 1) >= len(instructions):
                break

        errors = read_chunk_from_process(process.stderr)
        output = read_chunk_from_process(process.stdout)

        # if its not test mode, its print the process flow
        if not in_test_mode:
            print(colored(write_line, "green"))

            if errors is not None:
                print(colored(errors, "red"))

            print(output)

        # check that the process response how we expect
        if in_test_mode and not confirms_output(output, instructions[i + 1]):
            return False

        # increase the index by 2 if its test mode
        i += 2 if in_test_mode else 1

    return True


def confirms_output(origin, test):
    # check that the process response how we expect
    if origin != test:
        print(colored(test, "green"))
        print(colored("↑↑↑↑| Need-To-Be |↑↑↑↑", "green"))
        print(colored("↓↓↓↓| Actually   |↓↓↓↓", "red"))
        print(colored(origin, "red"))
        return False

    return True


def parse_head_line(head_line):
    """
    Return the 'read_first' flag and the 'test_mode' flag, by
    checking if the flags exist in the head line.
    """
    return READ_FIRST_FLAG in head_line, TEST_MODE_FLAG in head_line


def read_chunk_from_process(process_stream, attempts=3):
    """
    Reads (or at least try to read... three times by default) from process
    stream, in every try its sleep for 0.1s to let the process time to respond.
    return None in case of failure.
    """

    # if we read from the process with the 'read' function its will wait until the process is finish
    # this line disable that...
    fcntl.fcntl(process_stream, fcntl.F_SETFL, os.O_NONBLOCK)

    for i in range(attempts):
        try:
            # checks for any output
            output = process_stream.read()

            # if its find something
            if output is not None:
                clean_output = output.decode().strip()
                return clean_output

        except IOError:
            return None

        # gives the system its time to print
        time.sleep(.1)

    return None


def read_instructions_file(instructions_file_path):
    instructions_file = open(instructions_file_path, "r")

    # read the head line, to read the settings
    head_line = instructions_file.readline()
    # read all the file and filter by three quotes (like that - """text-to-pass-to-the-process""")
    instructions = re.findall('"""([^"]*)"""', instructions_file.read())

    instructions_file.close()
    return head_line, instructions


def active_command(parameters):
    """
    Responsible to extract all the necessary properties and active
    the right command.
    :param parameters: The params from the user (expect to a list like that: []).
    """
    if "-h" in parameters or "-help" in parameters:
        print(HELP)
        return

    if len(parameters) < 2:
        print("missing <process name> or <instruction file>.")
        return

    # read_instructions_file(parameters[INSTRUCTION_FILE_PATH])
    communicate_with_process(parameters[PROCESS_NAME], parameters[INSTRUCTION_FILE_PATH])
