#!/usr/bin/env python
# -*- coding: utf-8 -*-

from vestactrl import setup_digits, board_init_uart
import textwrap
import urllib2
import json
import time

def send_sign(text):
    """
    Wraps and sends text to the Vestaboard.
    """
    COLS = 22
    ROWS = 6

    # Wrap text to fit the board's width.
    lines = textwrap.wrap(text, width=COLS)

    # Truncate if the message is too long for the board's height.
    if len(lines) > ROWS:
        lines = lines[:ROWS]

    special_chars = {
        ' ': '`0',
        '\\w': '`1',  # white
        '\\r': '`2',  # red
        '\\o': '`3',  # orange
        '\\y': '`4',  # yellow
        '\\g': '`5',  # green
        '\\b': '`6',  # blue
        '\\v': '`7',  # violet
        '\\d': '`8',  # degree
        #      '`9',  # also degree
    }

    for code, color in special_chars.items():
        lines = [line.replace(code, color) for line in lines]

    # setup_digits handles displaying the lines on the board.
    # It will also vertically center the block of text.
    try:
        setup_digits(lines, left_to_right_swap=False, real_hw=True)
    except BaseException as e:
        print "Error setting digits:" + str(e)


def poll_and_display():
    """
    Polls the Protospace API and displays the sign message.
    """
    last_message = ""
    url = 'https://api.my.protospace.ca/stats/'

    while True:
        try:
            response = urllib2.urlopen(url)
            data = json.load(response)
            message = data.get('vestaboard')

            if message and message != last_message:
                print "Updating sign with new message: " + message
                send_sign(message.encode('utf-8'))
                last_message = message

        except (urllib2.URLError, ValueError, KeyError) as e:
            print "Error: {}".format(e)

        time.sleep(5)


if __name__ == '__main__':
    # Initialize communication with the board.
    board_init_uart()
    poll_and_display()
