__author__ = "Kenneth Pinkerton"

import signal
import os
import time
import logging
import errno
import argparse
from datetime import datetime as date_t


exit_flag = False
logging.basicConfig(level=logging.DEBUG,
                    format='%(axctime)s:%(levelname)s:%(message)s:%(threadName)s:')
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
    logger.error("Program was interupted by user command.")
    global exit_flag
    exit_flag = True


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--ext', type=str, default='.txt',
                        help='Text file extension to watch for.')
    parser.add_argument('-i', '--int', type=float, default=1.0,
                        help='Number of seconds between polling.')
    parser.add_argument('path', help='Directory to be watched.')
    parser.add_argument('magic', help='String to watch for.')


def main():

    green_flag = date_t.now()
    logger.info(
        '\n'
        '------------------------------\n'
        '   Running{0}\n'
        '   Started on {1}\n'
        '------------------------------\n'
        .format(__file__, green_flag.isoformat())
    )
    parser = create_parser()
    args = parser.parse_args()

    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    while not exit_flag:
        try:
            # try to call my directory watching function
            watcher(args)
        except OSError as ose:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            if ose.errno == errno.ENOENT:
                logger.error(f'{args.path} directory not found')
                time.sleep(1)
            else:
                logger.error(ose)

        except Exception as e:
            logger.error(f'UNHANDLED EXCEPTION:{e}')

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(int(float(args.interval)))

    # Final exit point
    # Notification of shutting down
    # Uptime from start to closing
    uptime = date_t.now() - green_flag
    logger.info(
        '\n'
        '------------------------------\n'
        '   Stopped {}\n'
        '   Uptime was {}\n'
        '------------------------------\n'
        .format(__file__, str(uptime))
    )
    logging.shutdown()

    if __name__ == "__main__":
        main()
