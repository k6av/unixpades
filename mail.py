"""
Mail script for Piqueserver.

Copyright (c) 2025 K6aV
License AGPLv3+: GNU AGPL version 3 or later <https://gnu.org/licenses/agpl.html>.
This script is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""

from piqueserver.commands import command, join_arguments
from piqueserver import commands
from piqueserver.config import config

import os
from os.path import realpath, join, commonprefix, isfile
from datetime import datetime, timezone

spool_dir = join(config.config_dir, 'mail')

def sendmail(spool_name, message):
    """
    Append `message` to spool `spool_name`.
    """
    spool_path = realpath(join(spool_dir, spool_name))
    if commonprefix((spool_path, spool_dir)) != spool_dir:
        raise Exception

    with open(spool_path, 'a') as spool:
        spool.write(message + "\n")

def getmail(spool_name):
    """
    Get all messages from spool `spool_name` and clear it.
    """
    spool_path = realpath(join(spool_dir, spool_name))
    if commonprefix((spool_path, spool_dir)) != spool_dir:
        raise Exception

    with open(spool_path, 'r') as spool:
        messages = spool.read()
    os.remove(spool_path)
    return messages

def hasmail(spool_name):
    """
    Checks whether spool `spool_name` has messages.
    """
    spool_path = realpath(join(spool_dir, spool_name))
    if commonprefix((spool_path, spool_dir)) != spool_dir:
        raise Exception

    return isfile(spool_path)

@command('sm', 'sendmail')
def cmd_sendmail(self, recipient=None, *args):
    """
    Send a message to another user.
    /sendmail <recipient> <message>
    """

    message_text = join_arguments(args)

    if recipient is None or len(recipient) == 0:
        self.send_chat("Please specify a recipient.")
        return
    if message_text is None or len(message_text) == 0:
        self.send_chat("Please specify a message.")
        return

    date_text = datetime.now(timezone.utc).strftime(r'%Y-%m-%d %H:%M:%S')
    message = f"{self.name} on {date_text} UTC: {message_text}"

    try:
        for player in self.protocol.players.values():
            if player.name == recipient:
                 player.send_chat(f"{self.name}: {message_text} (mail)")
                 return "Message sent to %s." % recipient

        sendmail(recipient, message)
    except:
        return "Message cannot be sent."

    return "Message sent to %s." % recipient

@command('mm', 'mail')
def cmd_getmail(self):
    """
    Read your mail and clear all messages.
    /mail
    """

    try:
        messages = getmail(self.name)
    except:
        return "You have no mail."

    return messages


def apply_script(protocol, connection, config):
    class MailConnection(connection):

        def on_login(self, name):
            if hasmail(self.name):
                self.send_chat("\5\u200bYou have mail.\6")
            else:
                self.send_chat("You have no mail.")
            return connection.on_login(self, name)

    return protocol, MailConnection
