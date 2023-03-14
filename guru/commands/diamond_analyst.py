import math

import pandas as pd
import re
import json
import os
import socket
from datetime import datetime

import guru.logger

COMMAND_NAME = "-diamond"

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

# diamond core address
HOST = "127.0.0.1"
PORT = 1829

# columns index in the Excel file
TRANSACTION_DATE = 0
WHOM = 1
THROUGH = 3
TYPE = 4
DEBIT_AMOUNT = 5
ORIGINAL_TRANSACTION_AMOUNT = 7
BILLING_DATE = 9
NOTE = 10

CARDS = {
    "9218": "[P]",
    "4712": "[M]"
}

log = []
printed_rows = 0

def remove_last_printed_row():
    print(LINE_UP, end=LINE_CLEAR)


def clean_printed_row():
    global printed_rows
    for i in range(printed_rows):
        remove_last_printed_row()

    printed_rows = 0


def print_msg(msg, color=None):
    global printed_rows
    if color is None:
        print(msg)
    else:
        guru.logger.simple_print(msg, color)

    size = os.get_terminal_size()
    printed_rows += math.ceil(len(msg) / size[0])


def expense_as_string(expense):
    # make it nice to the eye
    expense_through = CARDS[expense['through']] if expense['through'] in CARDS else f"C:[{expense['through']}]"
    expense_whom = expense['whom'].replace("BIT", "ביט")
    original_transaction_amount = "" if expense['originalTransactionAmount'] == expense['debitAmount'] else f"← ₪ {expense['originalTransactionAmount']}"
    debit_amount = f"₪ {expense['debitAmount']}"

    return f"{expense['id'] : <7}" \
           f"{expense['transactionDate'].strftime('%A, %d %b %Y') : <27}" \
           f"{debit_amount: <10} {original_transaction_amount : <12}" \
           f"{expense_whom: >50}   {expense_through : <8}   ~ {expense['note'] : <10}"


def parse_expense(excel_row):
    # read the parameters by the right index
    return {
        'id': "-",
        'through': excel_row[THROUGH],
        'whom': excel_row[WHOM],
        'transactionDate': datetime.strptime(excel_row[TRANSACTION_DATE], "%d-%m-%Y"),
        'billingDate': datetime.strptime(excel_row[BILLING_DATE], "%d-%m-%Y"),
        'debitAmount': excel_row[DEBIT_AMOUNT],
        'originalTransactionAmount': excel_row[ORIGINAL_TRANSACTION_AMOUNT],
        'note': excel_row[TYPE] if excel_row[NOTE] != excel_row[NOTE] else excel_row[NOTE] + ", " + excel_row[TYPE]
    }


def parse_user_flags(flags):
    # it's help to the search, because it's searching until the '@' or '#' character
    flags += "@"

    return {
        'tags': re.findall("@(.+?)\s*(?=[@#$])", flags),
        'budgets': re.findall("\$(.+?)\s*(?=[@#$])", flags),
        'note': re.findall("#(.+?)\s*(?=[@#$])", flags),
    }


def communicate(sock, msg):
    sock.sendall(json.dumps(msg).encode())
    data = json.loads(sock.recv(1024))

    log.append(f"Sent {json.dumps(msg)!r}")
    log.append(f"Received {data!r}")
    # guru.logger.simple_print(f"Sent {json.dumps(msg)!r}", "yellow")
    # guru.logger.simple_print(f"Received {data!r}", "yellow")

    return data


def read_and_save_tags(sock, tags):
    if len(tags) == 0:
        return []

    msg = {
        'type': "+tags",
        'in': {
            'names': tags
        }
    }

    data = communicate(sock, msg)
    return data['out']['tags']


def read_budget(sock, budgets):
    if len(budgets) == 0:
        return {'id': 1} # TODO: set default budget

    msg = {
        'type': "*budgets",
        'in': {
            'names': budgets
        }
    }

    data = communicate(sock, msg)

    try:
        return data['out']['budgets'][0]
    except IndexError:
        return {'id': 1}  # TODO: set default budget


def read_expense(sock, expenses):
    msg = {
        'type': "+expenses",
        'in': {
            'expenses': expenses,
        }
    }

    data = communicate(sock, msg)

    try:
        return data['out']['expenses'][0]['id']
    except IndexError and KeyError:
        return 0


def upload_to_diamond_core(sock, excel_expense, flags):
    tags = read_and_save_tags(sock, flags['tags'])
    budget = read_budget(sock, flags['budgets'])

    expense = {
        'debitAmount': excel_expense['debitAmount'],
        'whom': excel_expense['whom'],
        'through': excel_expense['through'],
        'payments': 1,
        'paymentsMade': 1,
        'expenseDate': int(excel_expense['billingDate'].timestamp()),
        'budgetId': budget['id'],
        'tagsIds': [tag['id'] for tag in tags],
    }

    return read_expense(sock, [expense])


def handle_command(command):
    if command == "q":
        clean_printed_row()
        exit(0)

    if command == "l":
        clean_printed_row()

        for i in range(len(log)):
            print_msg(f"{i}.  {log[i]}", "yellow")
            print_msg(f"------------------------------", "yellow")

        return True

    return False

def read_excel_file(filename, sheet_name, sock):
    # parse the Excel file
    global printed_rows
    df = pd.read_excel(filename, sheet_name=sheet_name)

    # run on all the Excel rows
    for excel_row in df.values:
        # if the cell is empty (he have the value of nan)
        if excel_row[0] != excel_row[0]:
            continue

        try:
            while True:
                expense = parse_expense(excel_row)
                print_msg(expense_as_string(expense), 'green')

                command = input(": ")
                printed_rows += 1
                clean_printed_row()
                handled = handle_command(command)

                if not handled:
                    break

            flags = parse_user_flags(command)
            expense_id = upload_to_diamond_core(sock, expense, flags)

            clean_printed_row()
            if expense_id > 0:
                expense['id'] = expense_id
                print(expense_as_string(expense))
            else:
                guru.logger.simple_print(expense_as_string(expense), 'red')


        except ValueError:
            pass


def analyze(filename, sock):
    read_excel_file(filename, 0, sock)
    read_excel_file(filename, 1, sock)
    read_excel_file(filename, 2, sock)


def active_command(parameters):
    # connect to the diamond core
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    print("diamond-core connected")

    analyze(parameters[0], sock)
