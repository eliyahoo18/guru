import fileinput


def replace_consent_from_file(path, origin_text, replacement):
    """
    replace the origin text with the replacement text if all the
    file.
    :param path: the path of the file.
    :param origin_text: the text that need do be replace.
    :param replacement: the text to replace with.
    """
    # open file to read and write and point to the beginning.
    file = open(path, "r+")
    # read all the file and replace what it's need.
    data = file.read().replace(origin_text, replacement)
    # remove all the old content of the file
    file.truncate(0)
    # and write it back to the file
    file.write(data)
    # close the file
    file.close()


