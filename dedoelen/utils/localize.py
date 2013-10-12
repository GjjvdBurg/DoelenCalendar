import locale
import logging
import sys

logger = logging.getLogger(__name__)

def set_locale():
    """
        Stel de taal van het programma in op Nederlands.
    """
    if sys.platform == 'win32':
        locale.setlocale(locale.LC_ALL, 'nld_nld')
    elif sys.platform == 'linux2':
        locale.setlocale(locale.LC_ALL, 'nl_NL.utf8')
