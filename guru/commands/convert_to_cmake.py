import os
import shutil
import ntpath

from termcolor import colored

from guru.commands.replace_content import replace_consent_from_file
from guru.logger import report_on_file, Action, report

COMMAND_NAME = "-to-cmake"
MULTIPLE_CONVERTS = "-all"
REPLACEMENT_LIST = {
    "what() const": "what() const noexcept",
    # Not ideal, but work fine... it's supposed to remove the one that added with the previous command
    "what() const noexcept noexcept": "what() const noexcept",
    "_exit(": "_Exit(",
}
EXTENSION_NECESSARY_FILES = [".cpp", ".c", ".h", ".hpp"]


def convert_all_to_cmake_projects(path):
    # Convert all the directories in this path
    for directory in os.listdir(path):
        # Get the full path of the current directory
        dirFullPath = f"{path}/{directory}"
        if not os.path.isdir(dirFullPath):
            continue

        try:
            # Report on start
            relativePath = os.path.relpath(dirFullPath, os.getcwd())
            print(f"Try converting '{relativePath}': ")

            # Get inside the current directory
            os.chdir(dirFullPath)
            convert_to_cmake_project(dirFullPath)

            # Report on finish
            print(f"'{relativePath}' successfully converted.")

        except Exception as e:
            report(e, Action.Error)


def convert_to_cmake_project(path):
    # confirm that the project need converting
    if "CMakeLists.txt" in os.listdir(path):
        raise Exception("Project already converted.")

    # Create the 'src' folder for all the code files
    os.popen('mkdir src').read()
    # Move the code files (.cpp / .h) to the 'src' directory, and remove the rest
    move_code_files(path, path + "/src")
    # Prepare the 'CMakeLists.txt' file
    create_cmake_list_file(path)
    # Run the cmake command to build the project
    build()


def move_code_files(path, src_path):
    """
    Moves all the cpp/h file to the 'src' folder and remove
    the rest.
    :param path: the rood of the directory.
    :param src_path: the path of the 'src' directory.
    """
    for file in os.listdir(path):
        # Save the full path
        fileFullPath = f"{path}/{file}"

        # so if one file failed it's will keep running
        try:
            if fileFullPath == src_path:
                # Prevent form removing the 'src' folder
                continue

            elif os.path.isdir(fileFullPath):
                # Move the code files (.cpp / .h) to the 'src' directory, and remove the rest
                move_code_files(fileFullPath, src_path)

                # Remove this empty folder
                shutil.rmtree(fileFullPath)
                report_on_file(fileFullPath, Action.Bad)

            else:
                # Move the code files (.cpp / .h) to the 'src' directory...
                fileName, extension = os.path.splitext(fileFullPath)
                if extension not in EXTENSION_NECESSARY_FILES:
                    # And remove the rest (Useless files...)
                    os.remove(fileFullPath)
                    report_on_file(fileFullPath, Action.Bad)

                elif os.path.exists(fileFullPath):
                    # Replace some line of code that work just with Window.
                    replace_necessary_code_line(fileFullPath)
                    # Move the file to the 'src' directory.
                    shutil.move(fileFullPath, src_path)
                    report_on_file(fileFullPath, Action.Fine)

        except (OSError, NotImplementedError):
            report_on_file(f"~ command on \"{fileFullPath}\" failed.", Action.Error)


def replace_necessary_code_line(path):
    """
    Replace some line of code that work just with Window.
    :param path: the path of the code file (.cpp/.h).
    """
    try:
        for replace_form, replace_to in REPLACEMENT_LIST.items():
            replace_consent_from_file(path, replace_form, replace_to)

    except ValueError as e:
        report_on_file(f"failed to read the file \"{path}\".", Action.Modify)


def create_cmake_list_file(path):
    """
    Create the 'CMakeLists.txt' file in the current working directory, and
    generate a default settings for it.
    :param path: The path af the root of the project
    """

    # Set the project name to be the name of the root directory
    projectName = ntpath.basename(path)
    CMakeListsFile = open("CMakeLists.txt", "w+")

    # Right down the default cmake list command.
    CMakeListsFile.write("cmake_minimum_required(VERSION 3.20)\n")
    CMakeListsFile.write("project(" + projectName + ")\n")
    CMakeListsFile.write("set(CMAKE_CXX_STANDARD 14)\n")
    CMakeListsFile.write("add_executable(" + projectName + " \n")
    for file in os.listdir(path + "/src"):
        CMakeListsFile.write("\t\tsrc/" + file + "\n")
    CMakeListsFile.write(")\n")

    CMakeListsFile.close()


def build():
    """
    Create the 'cmake' necessary directories and
    files, and builds the project
    """
    print(os.popen('mkdir cmake-build-debug;cd cmake-build-debug;cmake ..;make').read())


def active_command(parameters):
    """
    Responsible to extract all the necessary properties and active
    the right command.
    :param parameters: The params from the user (expect to a list like that: ['-all']).
    """
    rootPath = os.getcwd()

    if MULTIPLE_CONVERTS in parameters:
        # Confirms action
        if input(f"Are you sure you wont to convert {colored('all the folders', 'red')} in this directory '{os.path.basename(rootPath)}' (y/n)? ") != 'y':
            print("OK Cool, by.")
            return

        # Run on all the folders in the current directory (for converting multiple projects in once)
        convert_all_to_cmake_projects(rootPath)
        return

    # Confirms action
    if input(f"Are you sure you wont to convert {colored('this specific', 'red')} directory '{os.path.basename(rootPath)}' (y/n)? ") != 'y':
        print("OK Cool, by.")
        return

    # Run just on the current directory
    convert_to_cmake_project(rootPath)
