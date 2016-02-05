# -*- coding: utf-8 -*-
"""teax dangerous code snippets"""

import os

from teax import tty

def show_messages(messages):
    T_MESSAGE_APPENDIX = 4 * ' ' + '$[BG_WHITE]$[BLACK] {0} $[NORMAL]'

    def __find_meta(message):
        data = []
        if message.filename:
            data.append('file ' + os.path.split(message.filename)[1])
        if message.lineno:
            data.append('line ' + str(message.lineno))
        return data

    def __loop(messages):
        for message in messages:
            tty.warn(message.msg)
            meta = __find_meta(message)
            if meta:
                tty.echo(T_MESSAGE_APPENDIX.format('; '.join(meta)))

    tty.section('RESULT')
    __loop(messages)
