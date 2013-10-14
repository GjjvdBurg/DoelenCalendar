"""
This file contains the configuration options of the program and the code
necessary to create a :class:`Settings` instance.

"""

import pytz

class Settings(object):
        """
        A :class:`Settings` instance contains the configuration for the program.

        :param AMSTERDAM: timezone information for Europe/Amsterdam
        :type AMSTERDAM: :class:`pytz.timezone`
        :param FEED_URL: address of the RSS feed
        :type FEED_URL: str
        :param OUTFILE: path of the output file
        :type OUTFILE: str
        """
        def __init__(self, **entries):
            self.__dict__.update(entries)

__config__ = {
        'AMSTERDAM': pytz.timezone('Europe/Amsterdam'),
        'FEED_URL': '',
        'OUTFILE': ''
}

settings = Settings(**__config__)
