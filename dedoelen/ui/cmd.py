
import argparse
import logging

import dedoelen

from dedoelen.core import calendar
from dedoelen.core import scraper
from dedoelen.core import parser
from dedoelen.core import update
from dedoelen.core.conf import settings
from dedoelen.utils.localize import set_locale
from dedoelen.utils.log import init_logger

class Main(object):
    def __init__(self):
        set_locale()
        self.version = dedoelen.get_version()

    def parse_cmdline(self):
        argp = argparse.ArgumentParser()
        argp.add_argument("action", 
                help="specify the action to perform (init|update)")
        argp.add_argument("-v", "--verbose", action="store_true", 
                help="increase output verbosity")
        args = argp.parse_args()
        if args.verbose:
            init_logger("INFO")
        else:
            init_logger("ERROR")
        logger = logging.getLogger(__name__)
        if args.action == 'init':
            logger.info("Running action initialize")
            self.initialize()
        elif args.action == 'update':
            logger.info("Running action update")
            self.update()
        else:
            raise ValueError("action can be either 'init' or 'update'")

    def initialize(self):
        urls = scraper.scrape_rss()
        urls = urls[:20]
        pages = scraper.scrape_html(urls)
        voorstellingen = [parser.html2voorstelling(x) for x in pages]
        voorstellingen = [x for x in voorstellingen if x is not None]
        cal = calendar.make_calendar(voorstellingen)
        self.write_cal(cal)

    def update(self):
        urls = scraper.scrape_rss()
        pages = scraper.scrape_html(urls)
        voorstellingen = [parser.html2voorstelling(x) for x in pages]
        voorstellingen = [x for x in voorstellingen if x is not None]
        voorstellingen = update.update_voorstellingen(voorstellingen)
        cal = calendar.make_calendar(voorstellingen)
        self.write_cal(cal)

    def write_cal(self, calendar):
        with open(settings.OUTFILE, "wb") as fid:
            fid.write(calendar.to_ical())

    def __call__(self):
        try:
            return self.parse_cmdline()
        except KeyboardInterrupt:
            print("*** interrupted")
            return 2


