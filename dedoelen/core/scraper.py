
"""
In this file all functions related to scraping are defined.
"""

import cookielib
import feedparser
import logging
import mechanize
import time

from urllib2 import URLError

from dedoelen.core.conf import settings
from dedoelen.utils.progress import ophaal_progress

logger = logging.getLogger(__name__)

def scrape_rss():
    """
        Scrape the RSS feed for urls. All urls are collected and returned.

        :returns: urls scraped from RSS feed
        :rtype: list
    """
    feed = feedparser.parse(settings.FEED_URL)
    urls = []
    for entry in feed.entries:
        urls.append(entry.link)
    logger.info("Scraped %i urls from the RSS feed." % len(urls))
    return urls

def scrape_html(urls):
    """
        Get all pages given by the :attr:`urls`. If the server returns an error
        when too many requests are placed, a 10 second wait is performed. If an
        error occurs when getting the page a 5 second wait is performed and a
        warning is logged. All pages are returned as (page, url) tuples.

        :param urls: urls of De Doelen events
        :type urls: list
        :returns: tuples of html pages and the corresponding url
        :rtype: list
    """
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    br.add_headers = [('User-agent', 'Mozilla/5.0 (X11; U; Linux x86_64;\
            rv; 18.0) Gecko/20100101 Firefox/18.0')]

    pages = []
    ophaal_progress.maxval = len(urls)
    ophaal_progress.start()
    count = 0
    for url in urls:
        while True:
            try:
                response = br.open(url)
                page = response.read()
                if 'overlast van SPAM-bots' in page:
                    time.sleep(10)
                    continue
                break
            except URLError as exc:
                wrn = (
                        "Er is een fout opgetreden bij het ophalen van de "
                        "pagina (%s). We proberen het over 5 seconden opnieuw. "
                        "De URLError is: %s" % (url, exc.reason))
                logger.warning(wrn)
                time.sleep(5)
                continue
        pages.append((url, page))
        logger.info("Successfully scraped url: %s" % url)
        count += 1
        ophaal_progress.update(count)
    ophaal_progress.finish()
    return pages