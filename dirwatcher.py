__author__ = "Kenneth Pinkerton"

import signal
import os
import time
import logging
import errno
import argparse
from datetime import datetime as date_t


exit_flag = False
logger = logging.getLogger(__file__)
files = {}


def watcher(args):
    logger.info('Watching directory: {}, File Extension: {}, Every {} second, Magic Text is: {}'.format(
        args.path, args.ext, args.interval, args.magic))
    file_list = os.listdir(args.path)
    for f in file_list:
        if f.endswith(args.text) and f not in files:
            files[f] = 0
            logger.info(f"{f} added to watchlist.")
    for f in list(files):
        if f not in file_list:
            logger.info(f"{f} no longer in watchlist.")
            del files[f]
    for f in files:
        files[f] = find_magic(
            os.path.join(args.path, f), files[f], args.magic
        )


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name
    logger.warn('Received ' + signal.Signals(sig_num).name)
    exit_flag = True


def main():
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    while not exit_flag:
        try:
            # call my directory watching function
            pass
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            pass

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(polling_interval)

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start
