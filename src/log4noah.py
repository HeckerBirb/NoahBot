import os
from dataclasses import dataclass
from datetime import datetime

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()


@dataclass
class BotLogger:
    _log_level: int

    def _log_msg(self, log_level: str, msg: str):
        if _get_log_level(log_level) < self._log_level:
            return

        now = str(datetime.now()).split('.')[0]
        print(f'{now} [{log_level}]: {msg}')

    def debug(self, log_message: str = ''):
        """
        Debug messages to help narrow down a particular problem with communication or the bot itself.
        Args:
            log_message: message to be logged.
        """
        self._log_msg('DEBUG', log_message)

    def info(self, log_message: str = ''):
        """
        Informational messages for example updates of regular program flows or successful, regular events.
        Args:
            log_message: message to be logged.
        """
        self._log_msg('INFO', log_message)

    def warn(self, log_message: str = ''):
        """
        Warning messages indicating a potential problem which may at a later point cause an error of some magnitude.
        Args:
            log_message: message to be logged.
        """
        self._log_msg('WARN', log_message)

    def error(self, log_message: str = 'Error!'):
        """
        For errors which indicate a problem, however not one that causes downtime or security issues.
        Args:
            log_message: message to be logged.
        """
        self._log_msg('ERROR', log_message)

    def critical(self, log_message: str = 'Critical error!'):
        """
        For CRITICAL errors which cause immediate interruption of service or security threats. Consider pulling the plug!
        Args:
            log_message: message to be logged.
        """
        self._log_msg('CRITICAL', log_message)


def _get_log_level(level):
    return {
        'DEBUG': 0,
        'INFO': 1,
        'WARN': 2,
        'ERROR': 3,
        'CRITICAL': 4
    }.get(level, 'INFO')


STDOUT_LOG = BotLogger(_get_log_level(LOG_LEVEL))
