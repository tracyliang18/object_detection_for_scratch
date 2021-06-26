# -*- coding: utf-8 -*-
import logging
import os
import sys
import contextlib

_all_loggers = []
_default_level_name = os.getenv('LOGGING_LEVEL', 'INFO')
_default_level = logging.getLevelName(_default_level_name.upper())

def set_output_file(fout, mode='a'):
    """set log output file

    :type fout: str or file-like
    :param fout: file-like object that supports write and flush, or string for
        the filename
    :param mode: specify the mode to open log file if *fout* is a string"""
    if isinstance(fout, str):
        fout = open(fout, mode)
    LogFormatter.log_fout = fout

class LogFormatter(logging.Formatter):
    log_fout = None
    date_full = '[%(asctime)s %(lineno)d@%(filename)s:%(name)s] '
    date = '%(asctime)s '
    msg = '%(message)s'
    max_lines = 256

    def _color_exc(self, msg):
        return '\x1b[34m{}\x1b[0m'.format(msg)

    def _color_dbg(self, msg):
        return '\x1b[36m{}\x1b[0m'.format(msg)

    def _color_warn(self, msg):
        return '\x1b[1;31m{}\x1b[0m'.format(msg)

    def _color_err(self, msg):
        return '\x1b[1;4;31m{}\x1b[0m'.format(msg)

    def _color_omitted(self, msg):
        return '\x1b[35m{}\x1b[0m'.format(msg)

    def _color_normal(self, msg):
        return msg

    def _color_date(self, msg):
        return '\x1b[32m{}\x1b[0m'.format(msg)

    def format(self, record):
        if record.levelno == logging.DEBUG:
            mcl, mtxt = self._color_dbg, 'DBG'
        elif record.levelno == logging.WARNING:
            mcl, mtxt = self._color_warn, 'WRN'
        elif record.levelno == logging.ERROR:
            mcl, mtxt = self._color_err, 'ERR'
        else:
            mcl, mtxt = self._color_normal, ''

        if mtxt:
            mtxt += ' '

        if self.log_fout:
            self.__set_fmt(self.date_full + mtxt + self.msg)
            formatted = super(LogFormatter, self).format(record)
            nr_line = formatted.count('\n') + 1
            if nr_line >= self.max_lines:
                head, body = formatted.split('\n', 1)
                formatted = '\n'.join([
                    head,
                    'BEGIN_LONG_LOG_{}_LINES{{'.format(nr_line - 1),
                    body,
                    '}}END_LONG_LOG_{}_LINES'.format(nr_line - 1)
                ])
            self.log_fout.write(formatted)
            self.log_fout.write('\n')
            self.log_fout.flush()

        self.__set_fmt(self._color_date(self.date) + mcl(mtxt + self.msg))
        formatted = super(LogFormatter, self).format(record)

        if record.exc_text or record.exc_info:
            # handle exception format
            b = formatted.find('Traceback ')
            if b != -1:
                s = formatted[b:]
                s = self._color_exc('  ' + s.replace('\n', '\n  '))
                formatted = formatted[:b] + s

        nr_line = formatted.count('\n') + 1
        if nr_line >= self.max_lines:
            lines = formatted.split('\n')
            remain = self.max_lines//2
            removed = len(lines) - remain * 2
            if removed > 0:
                mid_msg = self._color_omitted(
                    '[{} log lines omitted (would be written to output file '
                    'if set_output_file() has been called;\n'
                    ' the threshold can be set at '
                    'LogFormatter.max_lines)]'.format(removed))
                formatted = '\n'.join(
                    lines[:remain] + [mid_msg] + lines[-remain:])

        return formatted


    if sys.version_info.major < 3:
        def __set_fmt(self, fmt):
            self._fmt = fmt
    else:
        def __set_fmt(self, fmt):
            self._style._fmt = fmt


def get_logger(name=None, formatter=LogFormatter):
    """get logger with given name"""

    logger = logging.getLogger(name)
    if getattr(logger, '_init_done__', None):
        return logger
    logger._init_done__ = True
    logger.propagate = False
    logger.setLevel(_default_level)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter(datefmt='%d %H:%M:%S'))
    handler.setLevel(0)
    del logger.handlers[:]
    logger.addHandler(handler)
    _all_loggers.append(logger)
    return logger

def set_default_level(level, update_existing=True):
    """set default logging level

    :param level: loggin level given by python :mod:`logging` module
    :param update_existing: whether to update existing loggers"""
    global _default_level
    _default_level = level
    if update_existing:
        for i in _all_loggers:
            i.setLevel(level)

_logger = get_logger(__name__)

def enable_debug_log():
    """set logging level to debug for all components"""
    set_default_level(logging.DEBUG)
