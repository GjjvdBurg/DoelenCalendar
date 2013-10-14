
"""
In this file all functions related to scraping are defined.
"""

import cookielib
import feedparser
import logging
import mechanize
import time

from httplib import IncompleteRead
from urllib2 import URLError

from dedoelen.core.conf import settings
from dedoelen.utils.progress import ophaal_progress

logger = logging.getLogger(__name__)

def scrape_rss():
    """
        Scrape the RSS feed for urls. All urls are collected and returned.

        :raises ValueError: when no urls are found in the feed.
        :returns: urls scraped from RSS feed
        :rtype: list
    """
    feed = feedparser.parse(settings.FEED_URL)
    urls = []
    for entry in feed.entries:
        urls.append(entry.link)
    logger.info("Scraped %i urls from the RSS feed." % len(urls))
    if len(urls) == 0:
        logger.critical("No urls found on RSS feed.")
        raise SystemExit
    return urls

def get_doelen_page(browser, url):
    """
        Get a single page from the web. Several warnings can occur in this
        process. An :class:`httplib.IncompleteRead` exception occurs when the
        request to the server is not completed, in this case a 5 second wait is
        allowed and the error is logged. After the wait the attempt is repeated.
        An :class:`urllib2.URLError` can also occur, it is handled in the same
        manner. Finally, a SPAM-bot page can be shown, which can happen when too
        many requests are made to the server. Luckily, this page includes the
        cookies required for a valid request, so when this page is encountered
        the next attempts do not suffer. To be fair, a 10 second wait is
        included after this error. When a page is retrieved succesfully, the
        loop breaks.

        :param browser: initialized browser instance
        :type browser: :class:`mechanize.Browser`
        :param url: url of the web page we want
        :type url: str
        :returns: webpage
        :rtype: str
    """
    while True:
        try:
            response = browser.open(url)
            page = response.read()
            if 'overlast van SPAM-bots' in page:
                print('overlast van SPAM-bots')
                time.sleep(10)
                continue
            break
        except IncompleteRead as exc:
            wrn = (
                    "Er is een fout opgetreden bij het ophalen van de pagina "
                    "(%s). We proberen het over 5 seconden opnieuw. "
                    "(IncompleteRead)" % url)
            logger.warning(wrn)
            time.sleep(5)
            continue
        except URLError as exc:
            print('Fout bij %s' % url)
            wrn = (
                    "Er is een fout opgetreden bij het ophalen van de "
                    "pagina (%s). We proberen het over 5 seconden opnieuw. "
                    "De URLError is: %s" % (url, exc.reason))
            logger.warning(wrn)
            time.sleep(5)
            continue
    return page

def scrape_html(urls):
    """
        Get all pages given by the :attr:`urls`. If the server returns an error
        when too many requests are placed, a 10 second wait is performed. If an
        error occurs when getting the page a 5 second wait is performed and a
        warning is logged. All pages are returned as (url, page) tuples. A
        progress bar is printed to show the total number of pages retrieved.

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
        page = get_doelen_page(br, url)
        pages.append((url, page))
        logger.info("Successfully scraped url: %s" % url)
        count += 1
        ophaal_progress.update(count)
    ophaal_progress.finish()
    return pages
